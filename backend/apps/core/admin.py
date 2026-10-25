from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.utils.html import format_html

from . import images
from .models import ContentPage, Destination, Lead, Partner


class DestinationForm(forms.ModelForm):
    hero_image = forms.ChoiceField(
        choices=[('', 'Default photo')] + images.choices(), required=False,
        help_text='The photo on this destination\'s card (menu, homepage, /destinations/).',
    )

    class Meta:
        model = Destination
        fields = '__all__'


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    form = DestinationForm
    list_display = ('name', 'slug', 'is_active', 'sort_order', 'page_count', 'published_count')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            page_total=Count('pages'), page_live=Count('pages', filter=Q(pages__status=ContentPage.Status.PUBLISHED)),
        )

    @admin.display(description='Pages', ordering='page_total')
    def page_count(self, obj):
        return obj.page_total

    @admin.display(description='Published', ordering='page_live')
    def published_count(self, obj):
        return obj.page_live


CAB_SUPPLY_WARNING = (
    'This cab page is live, but no active cab partner has agreed to receive referrals yet. Do not start cab ads until '
    'you have one: add a partner who offers cabs, is active and has a referral terms date.'
)


def warn_if_cab_supply_missing(modeladmin, request, page):
    """Module 08 rule 1: a cab page may go live early, but cab ads wait for confirmed cab partner supply."""
    if page.page_type == ContentPage.PageType.CAB and page.is_published and not Partner.cab_supply_confirmed():
        modeladmin.message_user(request, CAB_SUPPLY_WARNING, level=messages.WARNING)


@admin.action(description='Publish selected pages (checks the required fields)')
def publish_pages(modeladmin, request, queryset):
    published = 0
    for page in queryset.filter(status=ContentPage.Status.DRAFT):
        page.status = ContentPage.Status.PUBLISHED
        try:
            page.full_clean()
        except ValidationError as error:
            modeladmin.message_user(request, f'"{page.title}" not published: {"; ".join(error.messages)}', level='error')
            continue
        page.save()
        published += 1
        warn_if_cab_supply_missing(modeladmin, request, page)
    modeladmin.message_user(request, f'{published} page(s) published.')


@admin.action(description='Unpublish selected pages (back to draft)')
def unpublish_pages(modeladmin, request, queryset):
    count = queryset.filter(status=ContentPage.Status.PUBLISHED).update(status=ContentPage.Status.DRAFT)
    modeladmin.message_user(request, f'{count} page(s) unpublished.')


class ContentPageForm(forms.ModelForm):
    # A dropdown of the licensed photo library, so the alt text and credits always come with the photo.
    hero_image = forms.ChoiceField(
        choices=[('', 'Default photo for this page type')] + images.choices(), required=False,
        help_text='Photos are listed in apps/core/images.py with their credits; see /photo-credits/.',
    )

    class Meta:
        model = ContentPage
        fields = '__all__'


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    form = ContentPageForm
    list_display = ('title', 'page_type', 'status', 'destination', 'sort_order', 'updated_at', 'view_on_site')
    list_filter = ('status', 'page_type', 'destination')
    search_fields = ('title', 'slug', 'intro')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('published_at', 'updated_at')
    actions = [publish_pages, unpublish_pages]
    fieldsets = (
        (None, {'fields': ('page_type', 'title', 'slug', 'destination', 'status', 'sort_order', 'hero_image')}),
        ('Content', {'fields': ('intro', 'duration', 'body', 'itinerary', 'inclusions', 'exclusions', 'faq')}),
        ('Search engines', {'fields': ('meta_title', 'meta_description', 'canonical_override')}),
        ('Record', {'fields': ('published_at', 'updated_at', 'internal_notes')}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        warn_if_cab_supply_missing(self, request, obj)

    @admin.display(description='Live page')
    def view_on_site(self, obj):
        if not obj.is_published:
            return '-'
        return format_html('<a href="{}" target="_blank" rel="noopener">View</a>', obj.get_absolute_url())


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = (
        'business_name', 'contact_name', 'phone', 'offers_tours', 'offers_cabs', 'offers_homestays',
        'is_active', 'referral_terms_agreed_on', 'referrals', 'last_verified_at',
    )
    list_filter = ('is_active', 'offers_tours', 'offers_cabs', 'offers_homestays')
    search_fields = ('business_name', 'contact_name', 'phone', 'service_regions')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('business_name', 'contact_name', 'phone', 'whatsapp', 'is_active')}),
        ('Services', {'fields': ('offers_tours', 'offers_cabs', 'offers_homestays', 'service_regions', 'response_hours')}),
        ('Referral terms', {'fields': ('referral_terms_agreed_on', 'referral_terms_notes')}),
        ('Notes', {'fields': ('notes', 'last_verified_at')}),
        ('Record', {'fields': ('created_at', 'updated_at')}),
    )

    def get_queryset(self, request):
        counted = [s for s in Lead.Status.values if s not in (Lead.Status.SPAM, Lead.Status.INVALID)]
        return super().get_queryset(request).annotate(_referrals=Count('leads', filter=Q(leads__status__in=counted)))

    @admin.display(description='Referrals vs free pilot', ordering='_referrals')
    def referrals(self, obj):
        limit = settings.PILOT_REFERRALS_PER_PARTNER
        text = f'{obj._referrals} of {limit} free'
        return f'{text} - pilot used up' if obj._referrals >= limit else text


@admin.action(description='Mark selected new leads as qualified')
def mark_qualified(modeladmin, request, queryset):
    count = 0
    for lead in queryset.filter(status=Lead.Status.NEW):
        lead.status = Lead.Status.QUALIFIED
        lead.save()
        count += 1
    modeladmin.message_user(request, f'{count} lead(s) marked qualified.')


def _close_out(status, label):
    @admin.action(description=f'Mark selected as {label}')
    def action(modeladmin, request, queryset):
        count = 0
        for lead in queryset.filter(status__in=[Lead.Status.NEW, Lead.Status.QUALIFIED]):
            lead.status = status
            lead.save()
            count += 1
        modeladmin.message_user(request, f'{count} lead(s) marked {label}.')
    action.__name__ = f'mark_{status}'
    return action


mark_spam = _close_out(Lead.Status.SPAM, 'spam')
mark_invalid = _close_out(Lead.Status.INVALID, 'invalid')


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'phone', 'service_type', 'status', 'lead_channel', 'partner',
        'consent_given', 'is_duplicate', 'utm_campaign', 'created_at',
    )
    list_filter = ('status', 'lead_channel', 'service_type', 'consent_given', 'is_duplicate', 'utm_campaign')
    search_fields = ('name', 'phone')
    date_hierarchy = 'created_at'
    actions = [mark_qualified, mark_spam, mark_invalid]
    readonly_fields = (
        'consent_at', 'consent_notice_version',
        'landing_path', 'utm_source', 'utm_medium', 'utm_campaign', 'gclid',
        'created_at', 'qualified_at', 'referred_at', 'partner_responded_at',
    )
    fieldsets = (
        ('Enquiry', {'fields': ('name', 'phone', 'service_type', 'travel_date_or_month', 'travellers',
                                'pickup_city', 'budget', 'notes')}),
        ('Handling', {'fields': ('status', 'partner', 'lead_channel', 'is_duplicate', 'founder_notes')}),
        ('Consent to share with one partner', {'fields': ('consent_given', 'consent_source', 'consent_at',
                                                           'consent_notice_version')}),
        ('Attribution', {'fields': ('landing_path', 'utm_source', 'utm_medium', 'utm_campaign', 'gclid')}),
        ('Timeline', {'fields': ('created_at', 'qualified_at', 'referred_at', 'partner_responded_at')}),
    )

    def get_readonly_fields(self, request, obj=None):
        # The channel is chosen when the founder records a WhatsApp/phone lead; afterwards it is history.
        fields = super().get_readonly_fields(request, obj)
        return fields + ('lead_channel',) if obj else fields
