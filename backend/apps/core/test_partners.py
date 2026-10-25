from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Partner
from .validators import normalize_phone


def make_partner(**overrides):
    data = dict(business_name='Hill Cabs', phone='98765 43210', offers_cabs=True)
    data.update(overrides)
    return Partner.objects.create(**data)


class PhoneNormalisationTests(SimpleTestCase):
    def test_indian_mobile_formats_normalise_to_plus91(self):
        for raw in ('9876543210', '98765 43210', '+91 98765-43210', '919876543210', '09876543210', '(98765) 43210'):
            self.assertEqual(normalize_phone(raw), '+919876543210', raw)

    def test_international_numbers_need_plus_prefix(self):
        self.assertEqual(normalize_phone('+44 7700 900123'), '+447700900123')
        with self.assertRaises(ValidationError):
            normalize_phone('447700900123')

    def test_invalid_numbers_rejected(self):
        for raw in ('', '12345', '5876543210', 'abcdefghij', '+91 12345', '98765432101234'):
            with self.assertRaises(ValidationError, msg=raw):
                normalize_phone(raw)


class PartnerModelTests(TestCase):
    def test_phone_and_whatsapp_are_normalised_on_save(self):
        partner = make_partner(whatsapp='99999 88888')
        partner.refresh_from_db()
        self.assertEqual(partner.phone, '+919876543210')
        self.assertEqual(partner.whatsapp, '+919999988888')

    def test_blank_whatsapp_is_allowed(self):
        self.assertEqual(make_partner().whatsapp, '')

    def test_full_clean_rejects_bad_phone(self):
        with self.assertRaises(ValidationError) as ctx:
            Partner(business_name='X', phone='123', offers_tours=True).full_clean()
        self.assertIn('phone', ctx.exception.message_dict)

    def test_at_least_one_service_required(self):
        with self.assertRaises(ValidationError):
            Partner(business_name='X', phone='9876543210').full_clean()

    def test_can_receive_referrals_needs_active_and_agreed_terms(self):
        agreed = date(2026, 10, 28)
        cases = [
            (True, agreed, True),
            (True, None, False),     # no recorded referral-terms acknowledgement
            (False, agreed, False),  # deactivated
            (False, None, False),
        ]
        for is_active, terms, expected in cases:
            partner = make_partner(is_active=is_active, referral_terms_agreed_on=terms)
            self.assertEqual(partner.can_receive_referrals, expected, (is_active, terms))

    def test_str_is_business_name(self):
        self.assertEqual(str(make_partner(business_name='Araku Hills Tours')), 'Araku Hills Tours')


class PartnerAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser('owner', 'o@example.test', 'a-long-test-password-1')
        make_partner(business_name='Cab One', offers_cabs=True)
        make_partner(business_name='Tour One', offers_cabs=False, offers_tours=True)
        make_partner(business_name='Retired', is_active=False)

    def test_admin_requires_login(self):
        response = self.client.get(reverse('admin:core_partner_changelist'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_changelist_filters_by_service_and_active(self):
        self.client.force_login(self.owner)
        url = reverse('admin:core_partner_changelist')
        cabs = self.client.get(url, {'offers_cabs__exact': '1', 'is_active__exact': '1'})
        self.assertContains(cabs, 'Cab One')
        self.assertNotContains(cabs, 'Tour One')
        self.assertNotContains(cabs, 'Retired')

    def test_changelist_search_by_phone_and_name(self):
        self.client.force_login(self.owner)
        url = reverse('admin:core_partner_changelist')
        self.assertContains(self.client.get(url, {'q': 'Tour One'}), 'Tour One')
        self.assertContains(self.client.get(url, {'q': '9876543210'}), 'Cab One')

    def test_add_form_saves_partner(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('admin:core_partner_add'), {
            'business_name': 'New Homestay', 'phone': '90000 11111', 'offers_homestays': 'on', 'is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Partner.objects.get(business_name='New Homestay').phone, '+919000011111')


class PartnerPrivacyTests(TestCase):
    def test_partner_data_has_no_public_route(self):
        make_partner(business_name='Secret Cabs')
        for path in ('/partners/', '/partner/', '/api/partners/'):
            self.assertEqual(self.client.get(path).status_code, 404, path)
        # Partner details never appear on the public trust pages either.
        for name in ('core:contact', 'core:privacy', 'core:terms'):
            self.assertNotContains(self.client.get(reverse(name)), 'Secret Cabs')
