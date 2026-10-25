from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from . import content, images
from .validators import normalize_phone, validate_phone


class Partner(models.Model):
    """An independent tour/cab/homestay operator the founder refers leads to. Partners never log in (MVP)."""

    business_name = models.CharField(max_length=150)
    contact_name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, validators=[validate_phone])
    whatsapp = models.CharField(max_length=20, blank=True, validators=[validate_phone])
    service_regions = models.CharField(max_length=255, blank=True, help_text='Areas they serve, e.g. Vizag, Araku, Lambasingi.')
    offers_tours = models.BooleanField(default=False)
    offers_cabs = models.BooleanField(default=False)
    offers_homestays = models.BooleanField(default=False)
    response_hours = models.CharField(max_length=120, blank=True, help_text='When they can answer a customer.')
    is_active = models.BooleanField(default=True)
    referral_terms_agreed_on = models.DateField(
        null=True, blank=True,
        help_text='Date the partner agreed to receive referred enquiries. Required before any lead is assigned.',
    )
    referral_terms_notes = models.TextField(
        blank=True, help_text='What was agreed: free pilot size, fee if agreed, what counts as invalid/duplicate.',
    )
    notes = models.TextField(blank=True, help_text='Interview notes: vehicles, tours, dated sample quotes, licence supplied.')
    last_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['business_name']

    def __str__(self):
        return self.business_name

    @property
    def can_receive_referrals(self):
        return self.is_active and self.referral_terms_agreed_on is not None

    @classmethod
    def cab_supply_confirmed(cls):
        """True when at least one active cab partner has agreed to receive referrals (cab ads are gated on this, Module 08)."""
        return cls.objects.filter(offers_cabs=True, is_active=True, referral_terms_agreed_on__isnull=False).exists()

    def clean(self):
        if not (self.offers_tours or self.offers_cabs or self.offers_homestays):
            raise ValidationError('Select at least one service this partner offers (tours, cabs or homestays).')

    def save(self, *args, **kwargs):
        # Normalise so phone numbers compare and link consistently (wa.me needs the country code).
        self.phone = normalize_phone(self.phone)
        if self.whatsapp:
            self.whatsapp = normalize_phone(self.whatsapp)
        super().save(*args, **kwargs)


class Lead(models.Model):
    """A travel enquiry: from the short form, or entered by the founder for a WhatsApp/phone enquiry.

    Lead data is private: it is shown only in Django admin and never returned by any public route.
    """

    class ServiceType(models.TextChoices):
        TOUR = 'tour', 'Tour package'
        CAB = 'cab', 'Cab'

    class Status(models.TextChoices):
        NEW = 'new', 'New'
        QUALIFIED = 'qualified', 'Qualified'
        REFERRED = 'referred', 'Referred to partner'
        PARTNER_RESPONDED = 'partner_responded', 'Partner responded'
        WON = 'won', 'Won'
        LOST = 'lost', 'Lost'
        SPAM = 'spam', 'Spam'
        INVALID = 'invalid', 'Invalid'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    class Channel(models.TextChoices):
        FORM = 'form', 'Website form'
        WHATSAPP = 'whatsapp', 'WhatsApp (confirmed)'
        CALL = 'call', 'Phone call'
        MANUAL = 'manual', 'Manual entry'

    class ConsentSource(models.TextChoices):
        FORM = 'form', 'Website form checkbox'
        WHATSAPP_REPLY = 'whatsapp_reply', 'WhatsApp reply (YES)'
        CALL = 'call', 'Phone call'
        MANUAL = 'manual', 'Manual (other)'

    # Statuses that stamp a timestamp the first time they are reached.
    STAMPS = {
        Status.QUALIFIED: 'qualified_at',
        Status.REFERRED: 'referred_at',
        Status.PARTNER_RESPONDED: 'partner_responded_at',
    }
    # A lead in one of these can never be handed to a partner.
    NOT_REFERRABLE = (Status.SPAM, Status.INVALID, Status.WITHDRAWN)

    # What the traveller told us
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, validators=[validate_phone])
    service_type = models.CharField(max_length=10, choices=ServiceType.choices)
    travel_date_or_month = models.CharField(max_length=60)
    travellers = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    pickup_city = models.CharField(max_length=80, blank=True)
    # Free text on purpose: visitors write "around 20k", "15000-20000". Not money we compute with.
    budget = models.CharField(max_length=60, blank=True)
    notes = models.TextField(blank=True)

    # Handling
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    partner = models.ForeignKey(Partner, null=True, blank=True, on_delete=models.PROTECT, related_name='leads')
    lead_channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.MANUAL)
    is_duplicate = models.BooleanField(default=False, help_text='Same phone + service within the duplicate window.')
    founder_notes = models.TextField(blank=True)

    # Attribution (filled from the session by Module 06; blank is fine)
    landing_path = models.CharField(max_length=200, blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    gclid = models.CharField(max_length=255, blank=True)

    # Consent to share details with ONE selected partner (CLAUDE.md invariant 1)
    consent_given = models.BooleanField(default=False)
    consent_at = models.DateTimeField(null=True, blank=True)
    consent_notice_version = models.CharField(max_length=40, blank=True)
    consent_source = models.CharField(max_length=20, choices=ConsentSource.choices, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    qualified_at = models.DateTimeField(null=True, blank=True)
    referred_at = models.DateTimeField(null=True, blank=True)
    partner_responded_at = models.DateTimeField(null=True, blank=True)

    _original_partner_id = None

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['phone', 'service_type', 'created_at']),
        ]

    def __str__(self):
        return f'Lead #{self.pk} {self.name} ({self.get_service_type_display()})'

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._original_partner_id = instance.partner_id
        return instance

    @classmethod
    def is_duplicate_submission(cls, phone, service_type):
        """True if a real (non-spam, non-invalid) lead with this phone + service exists inside the window."""
        since = timezone.now() - timedelta(hours=settings.LEAD_DUPLICATE_WINDOW_HOURS)
        return (
            cls.objects.filter(phone=phone, service_type=service_type, created_at__gte=since)
            .exclude(status__in=[cls.Status.SPAM, cls.Status.INVALID])
            .exists()
        )

    def _check_partner_assignment(self):
        """A partner can only be newly assigned with consent, to a ready partner, on a referrable lead."""
        if not self.partner_id or self.partner_id == self._original_partner_id:
            return
        if not self.consent_given:
            raise ValidationError({'partner': 'Cannot assign a partner: this lead has not consented to sharing.'})
        if self.status in self.NOT_REFERRABLE:
            raise ValidationError({'partner': f'Cannot assign a partner to a lead marked {self.get_status_display()}.'})
        if not self.partner.can_receive_referrals:
            raise ValidationError({
                'partner': 'This partner is inactive or has no recorded referral-terms acknowledgement.',
            })

    def clean(self):
        if self.consent_given and not self.consent_source:
            raise ValidationError({'consent_source': 'Say how consent was given (form, WhatsApp reply, call...).'})
        self._check_partner_assignment()

    def save(self, *args, **kwargs):
        self.phone = normalize_phone(self.phone)
        self._check_partner_assignment()

        now = timezone.now()
        if self.consent_given:
            if self.consent_at is None:
                self.consent_at = now
            if not self.consent_notice_version:
                self.consent_notice_version = settings.CONSENT_NOTICE_VERSION

        # Assigning a partner is the referral.
        if self.partner_id and self.status in (self.Status.NEW, self.Status.QUALIFIED):
            self.status = self.Status.REFERRED

        stamp_field = self.STAMPS.get(self.status)
        if stamp_field and getattr(self, stamp_field) is None:
            setattr(self, stamp_field, now)

        super().save(*args, **kwargs)
        self._original_partner_id = self.partner_id


class Destination(models.Model):
    """A place we cover (Araku Valley, Vizag, Lambasingi...). Pages can be grouped under one."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    summary = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, help_text='Inactive destinations are hidden from the menu and /destinations/.')
    sort_order = models.PositiveSmallIntegerField(default=100, help_text='Lower numbers are listed first.')
    hero_image = models.CharField(
        max_length=40, blank=True,
        help_text='A photo from the site library (apps/core/images.py) for its card. Blank = the default photo.',
    )

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def clean(self):
        if self.hero_image and not images.exists(self.hero_image):
            raise ValidationError({'hero_image': 'Choose a photo from the list.'})

    @property
    def hero_key(self):
        return self.hero_image or images.DEFAULT_HERO


# URLs served by other routes. A page may not take one of these slugs (the admin path is checked separately).
RESERVED_SLUGS = frozenset({
    'admin', 'static', 'media', 'health', 'contact', 'privacy', 'terms', 'enquiry', 'thank-you',
    'sitemap', 'robots', 'home', 'photo-credits', 'destinations',
})


class ContentPageQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status='published')


class ContentPage(models.Model):
    """An editable public page: the homepage, a tour/cab landing page, or a guide.

    There are deliberately no price fields. Pages never state a price; they invite a free quote instead
    (CLAUDE.md invariant 3).
    """

    class PageType(models.TextChoices):
        HOME = 'home', 'Homepage (exactly one)'
        PACKAGE = 'package', 'Tour package page'
        CAB = 'cab', 'Cab page'
        GUIDE = 'guide', 'Guide'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft (not public)'
        PUBLISHED = 'published', 'Published'

    destination = models.ForeignKey(Destination, null=True, blank=True, on_delete=models.SET_NULL, related_name='pages')
    page_type = models.CharField(max_length=10, choices=PageType.choices)
    title = models.CharField(max_length=150, help_text='Shown as the page heading. Match what people search for.')
    slug = models.SlugField(
        unique=True, help_text='The page address, e.g. araku-tour-packages. The homepage always uses "home".',
    )
    sort_order = models.PositiveSmallIntegerField(default=100, help_text='Lower numbers are listed first on the homepage.')
    intro = models.TextField(blank=True, help_text='Opening paragraph. Say plainly that independent partners send the quotes.')
    duration = models.CharField(max_length=80, blank=True, help_text='e.g. "Day trip, or 2 days / 1 night".')
    body = models.TextField(blank=True, help_text='Paragraphs separated by a blank line. Plain text only.')
    itinerary = models.TextField(
        blank=True,
        help_text='Blocks separated by a blank line. First line = heading (e.g. "Day 1: Vizag to Araku"), next lines = details.',
    )
    inclusions = models.TextField(blank=True, help_text='One item per line. Only what operators have confirmed.')
    exclusions = models.TextField(blank=True, help_text='One item per line.')
    faq = models.TextField(
        blank=True, help_text='Blocks separated by a blank line. First line = the question, next lines = the answer.',
    )
    hero_image = models.CharField(
        max_length=40, blank=True,
        help_text='A photo from the site library (apps/core/images.py). Blank = a default photo for this page type.',
    )
    meta_title = models.CharField(
        max_length=70, blank=True, help_text='Search-result title. Blank = "<title> | <site name>".',
    )
    meta_description = models.CharField(
        max_length=170, blank=True, help_text='Search-result description. Required to publish.',
    )
    canonical_override = models.CharField(
        max_length=300, blank=True, help_text='Rarely needed. A full https:// URL, or a path starting with /.',
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    internal_notes = models.TextField(blank=True, help_text='Never shown on the site: sources, things to verify.')

    objects = ContentPageQuerySet.as_manager()

    class Meta:
        ordering = ['sort_order', 'title']
        constraints = [
            models.UniqueConstraint(
                fields=['page_type'], condition=models.Q(page_type='home'), name='only_one_homepage',
            ),
        ]

    def __str__(self):
        return self.title

    # --- display helpers -------------------------------------------------
    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    @property
    def effective_title(self):
        return self.meta_title or self.title

    @property
    def paragraphs(self):
        return content.parse_paragraphs(self.body)

    @property
    def itinerary_blocks(self):
        return content.parse_blocks(self.itinerary)

    @property
    def inclusion_items(self):
        return content.parse_list(self.inclusions)

    @property
    def exclusion_items(self):
        return content.parse_list(self.exclusions)

    @property
    def faq_blocks(self):
        return content.parse_blocks(self.faq)

    @property
    def hero_key(self):
        """The photo for this page's banner and cards: its own choice, else a default for its type."""
        return self.hero_image or images.DEFAULT_FOR_TYPE[self.page_type]

    @property
    def has_form(self):
        return self.page_type in (self.PageType.HOME, self.PageType.PACKAGE, self.PageType.CAB)

    @property
    def cta_href(self):
        """Where "Get free quotes" leads: the form on this page, or the standalone enquiry page for guides."""
        return '#quote' if self.has_form else reverse('core:enquiry')

    @property
    def form_service(self):
        return {self.PageType.PACKAGE: 'tour', self.PageType.CAB: 'cab'}.get(self.page_type, '')

    @property
    def whatsapp_prefill(self):
        """Generic and non-sensitive: only the page's own title. Blank means "use the site default"."""
        return '' if self.page_type == self.PageType.HOME else f'Hi, I want a quote for {self.title}.'

    def get_absolute_url(self):
        if self.page_type == self.PageType.HOME:
            return reverse('core:home')
        return reverse('core:content_page', args=[self.slug])

    def canonical_url(self, base_url):
        base = base_url.rstrip('/')
        override = self.canonical_override.strip()
        if override.startswith('/'):
            return base + override
        return override or base + self.get_absolute_url()

    # --- validation ------------------------------------------------------
    def clean(self):
        errors = {}
        if self.page_type != self.PageType.HOME:
            admin_root = settings.ADMIN_URL_PATH.strip('/').split('/')[0]
            if self.slug in RESERVED_SLUGS or self.slug == admin_root:
                errors['slug'] = f'"{self.slug}" is used by another part of the site. Choose a different address.'

        override = self.canonical_override.strip()
        if override and not (override.startswith('/') or override.startswith('https://')):
            errors['canonical_override'] = 'Use a full https:// URL, or a path starting with /.'

        if self.hero_image and not images.exists(self.hero_image):
            errors['hero_image'] = 'Choose a photo from the list.'

        # Search results need distinct titles and descriptions, so duplicates are refused up front.
        others = ContentPage.objects.exclude(pk=self.pk)
        if self.effective_title and any(
            other.effective_title.casefold() == self.effective_title.casefold() for other in others
        ):
            errors['meta_title'] = 'Another page already has this search title. Make it unique.'
        if self.meta_description and others.filter(meta_description__iexact=self.meta_description).exists():
            errors['meta_description'] = 'Another page already has this search description. Make it unique.'

        if self.is_published:
            if not self.meta_description:
                errors.setdefault('meta_description', 'A search description is required before publishing.')
            if not self.intro:
                errors['intro'] = 'An introduction is required before publishing.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.page_type == self.PageType.HOME:
            self.slug = 'home'
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
