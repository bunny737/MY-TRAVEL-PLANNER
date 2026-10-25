"""The Django admin with a mandatory second factor (owner decision 2026-10-25: django-otp, authenticator app).

The admin holds travellers' phone numbers (CLAUDE.md invariant 4), so a password alone is not enough in production.

Flow: the normal admin password login -> /<admin>/mfa/ -> the 6-digit code from an authenticator app -> the admin.
A staff user who has no authenticator yet is shown a QR code once and must confirm a code from it. After that, a new
authenticator can only be added once `python manage.py reset_admin_mfa <username>` has been run on the server, so a
stolen password can never enrol an attacker's phone. Codes are throttled per device by django-otp (each wrong code
doubles the wait). Switched on by ADMIN_REQUIRE_MFA, which production forces on (config/settings/prod.py).
"""
from base64 import b32encode

import django_otp
import qrcode
import qrcode.image.svg
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.http import url_has_allowed_host_and_scheme, urlencode
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.cache import never_cache
from django_otp.plugins.otp_totp.models import TOTPDevice

DEVICE_NAME = 'Authenticator app'


class TokenForm(forms.Form):
    token = forms.CharField(
        label='6-digit code', max_length=10,
        widget=forms.TextInput(attrs={
            'autocomplete': 'one-time-code', 'inputmode': 'numeric', 'autofocus': True, 'size': 8,
        }),
    )

    def clean_token(self):
        token = self.cleaned_data['token'].replace(' ', '')
        if not token.isdigit():
            raise forms.ValidationError('Enter the numbers shown in your authenticator app.')
        return token


def _qr_svg(data):
    """An inline SVG QR code for the otpauth:// URL (generated here, so it never leaves the server)."""
    svg = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage, box_size=8).to_string(encoding='unicode')
    return mark_safe(svg[svg.index('<svg'):])  # drop the XML declaration


def _grouped(secret):
    return ' '.join(secret[i:i + 4] for i in range(0, len(secret), 4))


class MfaAdminSite(admin.AdminSite):
    @staticmethod
    def _mfa_on():
        return settings.ADMIN_REQUIRE_MFA

    @staticmethod
    def _password_ok(request):
        """Signed in with a password as staff (the second factor may still be missing)."""
        user = request.user
        return user.is_authenticated and user.is_active and user.is_staff

    def has_permission(self, request):
        if not super().has_permission(request):
            return False
        return not self._mfa_on() or request.user.is_verified()

    def login(self, request, extra_context=None):
        # Password already accepted but no code yet: go straight to the code step instead of the password form again.
        if request.method == 'GET' and self._mfa_on() and self._password_ok(request) and not request.user.is_verified():
            target = reverse('admin:mfa', current_app=self.name)
            next_url = request.GET.get('next')
            return redirect(f'{target}?{urlencode({"next": next_url})}' if next_url else target)
        return super().login(request, extra_context)

    def get_urls(self):
        return [path('mfa/', self.mfa_view, name='mfa')] + super().get_urls()

    def _safe_next(self, request):
        next_url = request.POST.get('next') or request.GET.get('next') or ''
        if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
            return next_url
        return reverse('admin:index', current_app=self.name)

    @method_decorator(never_cache)
    def mfa_view(self, request):
        next_url = self._safe_next(request)
        if not self._password_ok(request):
            return redirect_to_login(next_url, reverse('admin:login', current_app=self.name))
        user = request.user
        if not self._mfa_on() or user.is_verified():
            return redirect(next_url)

        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        enrolling = device is None
        if enrolling:
            # Only possible while the user has NO confirmed authenticator (first login, or after reset_admin_mfa).
            device = TOTPDevice.objects.filter(user=user, confirmed=False).first() or TOTPDevice.objects.create(
                user=user, name=DEVICE_NAME, confirmed=False,
            )

        form = TokenForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            allowed, _ = device.verify_is_allowed()  # checked first: a failed attempt below starts a new wait
            if device.verify_token(form.cleaned_data['token']):
                if enrolling:
                    device.confirmed = True
                    device.save(update_fields=['confirmed'])
                    TOTPDevice.objects.filter(user=user, confirmed=False).delete()
                django_otp.login(request, device)
                return redirect(next_url)
            form.add_error('token', 'That code is not right or has expired. Use the newest code.' if allowed else
                           'Too many wrong codes. Wait a little, then try the newest code.')

        context = {
            **self.each_context(request),
            'title': 'Set up two-step sign-in' if enrolling else 'Two-step sign-in',
            'form': form,
            'enrolling': enrolling,
            'next': next_url,
        }
        if enrolling:
            context['qr_svg'] = _qr_svg(device.config_url)
            context['secret'] = _grouped(b32encode(device.bin_key).decode())
        return render(request, 'admin/mfa.html', context)
