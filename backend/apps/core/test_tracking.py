from pathlib import Path

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .attribution import ATTRIBUTION_SESSION_KEY
from .middleware import AttributionMiddleware  # noqa: F401  (import check: the module exists and loads)
from .models import Lead
from .templatetags.cta import whatsapp_url
from .views import CONVERSION_PENDING

LOCMEM = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / 'static'

FORM = {
    'name': 'Asha Rao', 'phone': '9876543210', 'service_type': 'tour', 'travel_date_or_month': 'Dec', 'travellers': '4', 'consent_given': 'on',
}

ADS = dict(
    GA4_MEASUREMENT_ID='G-TEST123', GOOGLE_ADS_ID='AW-123456',
    GOOGLE_ADS_FORM_CONVERSION_LABEL='formLbl', GOOGLE_ADS_WHATSAPP_CONVERSION_LABEL='waLbl',
    GOOGLE_ADS_CALL_CONVERSION_LABEL='callLbl',
)
NO_TAGS = dict(
    GA4_MEASUREMENT_ID='', GOOGLE_ADS_ID='', GOOGLE_ADS_FORM_CONVERSION_LABEL='',
    GOOGLE_ADS_WHATSAPP_CONVERSION_LABEL='', GOOGLE_ADS_CALL_CONVERSION_LABEL='',
)

CAMPAIGN = '?utm_source=google&utm_medium=cpc&utm_campaign=Araku%20Search&gclid=Cj0abc_123'


class AttributionCaptureTests(TestCase):
    def attribution(self):
        return self.client.session.get(ATTRIBUTION_SESSION_KEY)

    def test_campaign_click_is_stored_with_path_only(self):
        self.client.get('/contact/' + CAMPAIGN)
        self.assertEqual(self.attribution(), {
            'landing_path': '/contact/', 'utm_source': 'google', 'utm_medium': 'cpc',
            'utm_campaign': 'Araku Search', 'gclid': 'Cj0abc_123',
        })
        self.assertNotIn('utm_source', self.attribution()['landing_path'])

    def test_later_visit_without_parameters_keeps_attribution(self):
        self.client.get('/contact/' + CAMPAIGN)
        self.client.get('/privacy/')
        self.assertEqual(self.attribution()['utm_campaign'], 'Araku Search')
        self.assertEqual(self.attribution()['landing_path'], '/contact/')

    def test_a_new_campaign_click_replaces_the_old_one_entirely(self):
        self.client.get('/contact/' + CAMPAIGN)
        self.client.get('/terms/?utm_source=newsletter')
        self.assertEqual(self.attribution(), {'landing_path': '/terms/', 'utm_source': 'newsletter'})

    def test_visit_without_parameters_creates_no_session(self):
        response = self.client.get('/contact/')
        self.assertNotIn('sessionid', response.cookies)
        self.assertIsNone(self.attribution())

    def test_partial_parameters_are_fine(self):
        self.client.get('/contact/?gclid=onlyclick')
        self.assertEqual(self.attribution(), {'landing_path': '/contact/', 'gclid': 'onlyclick'})

    def test_skipped_requests_store_nothing(self):
        self.client.get('/health/' + CAMPAIGN)
        self.client.get('/admin/login/' + CAMPAIGN)
        self.client.get('/static/css/site.css' + CAMPAIGN)
        self.client.post('/contact/' + CAMPAIGN)
        self.assertIsNone(self.attribution())

    def test_values_are_cleaned_truncated_and_last_duplicate_wins(self):
        self.client.get('/contact/', {'utm_source': ['first', 'sec\x00ond\x1f'], 'utm_campaign': 'c' * 500,
                                      'gclid': 'g' * 900})
        stored = self.attribution()
        self.assertEqual(stored['utm_source'], 'second')
        self.assertEqual(len(stored['utm_campaign']), 100)
        self.assertEqual(len(stored['gclid']), 255)

    def test_blank_parameters_do_not_overwrite(self):
        self.client.get('/contact/' + CAMPAIGN)
        self.client.get('/privacy/?utm_source=&gclid=%20')
        self.assertEqual(self.attribution()['utm_source'], 'google')


@override_settings(CACHES=LOCMEM, LEAD_FORM_THROTTLE='100/3600', LEAD_NOTIFY_EMAIL='')
class AttributionReachesLeadTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_campaign_click_then_form_gives_attributed_lead(self):
        self.client.get('/contact/' + CAMPAIGN)
        self.client.post(reverse('core:enquiry'), FORM)
        lead = Lead.objects.get()
        self.assertEqual(
            (lead.landing_path, lead.utm_source, lead.utm_medium, lead.utm_campaign, lead.gclid),
            ('/contact/', 'google', 'cpc', 'Araku Search', 'Cj0abc_123'),
        )

    def test_organic_lead_gets_landing_path_from_same_site_referer_without_query(self):
        self.client.post(reverse('core:enquiry'), FORM, HTTP_HOST='testserver',
                         HTTP_REFERER='http://testserver/privacy/?name=Asha&phone=98765')
        lead = Lead.objects.get()
        self.assertEqual(lead.landing_path, '/privacy/')
        self.assertEqual((lead.utm_source, lead.gclid), ('', ''))

    def test_external_referer_is_ignored(self):
        self.client.post(reverse('core:enquiry'), FORM, HTTP_REFERER='https://evil.example/page')
        self.assertEqual(Lead.objects.get().landing_path, '')


@override_settings(**NO_TAGS)
class TagsOffTests(TestCase):
    def test_no_tag_script_or_google_urls_without_ids(self):
        for name in ('core:contact', 'core:privacy', 'core:enquiry', 'core:thank_you'):
            html = self.client.get(reverse(name)).content.decode()
            self.assertNotIn('tracking.js', html, name)
            self.assertNotIn('googletagmanager', html, name)
            self.assertNotIn('data-tracking', html, name)

    def test_ads_send_to_is_empty_without_ids_and_labels(self):
        response = self.client.get(reverse('core:contact'))
        for key in ('ads_form_send_to', 'ads_whatsapp_send_to', 'ads_call_send_to'):
            self.assertEqual(response.context['tracking'][key], '')


@override_settings(**ADS)
class TagsOnTests(TestCase):
    def test_script_tag_carries_only_the_ids(self):
        html = self.client.get(reverse('core:contact')).content.decode()
        self.assertIn('js/tracking.js', html)
        self.assertIn('data-ga4-id="G-TEST123"', html)
        self.assertIn('data-ads-id="AW-123456"', html)
        self.assertNotIn('<script>', html)  # no inline script anywhere

    @override_settings(GOOGLE_ADS_ID='')
    def test_ga4_alone_is_enough(self):
        html = self.client.get(reverse('core:contact')).content.decode()
        self.assertIn('data-ga4-id="G-TEST123"', html)
        self.assertIn('data-ads-id=""', html)

    @override_settings(GA4_MEASUREMENT_ID='')
    def test_ads_alone_is_enough(self):
        self.assertIn('data-ads-id="AW-123456"', self.client.get(reverse('core:contact')).content.decode())

    def test_send_to_needs_both_ads_id_and_label(self):
        tracking = self.client.get(reverse('core:contact')).context['tracking']
        self.assertEqual(tracking['ads_form_send_to'], 'AW-123456/formLbl')
        self.assertEqual(tracking['ads_whatsapp_send_to'], 'AW-123456/waLbl')
        self.assertEqual(tracking['ads_call_send_to'], 'AW-123456/callLbl')
        with override_settings(GOOGLE_ADS_FORM_CONVERSION_LABEL=''):
            self.assertEqual(self.client.get(reverse('core:contact')).context['tracking']['ads_form_send_to'], '')

    def test_script_file_reports_the_three_planned_events_from_data_attributes_only(self):
        js = (STATIC_DIR / 'js' / 'tracking.js').read_text(encoding='utf-8')
        self.assertIn('generate_lead', js)
        self.assertIn("data-track", js)
        self.assertIn('data-ads-send-to', js)
        self.assertIn('data-lead-conversion', js)
        # Nothing is read from form fields, cookies or storage: no personal data can reach a tag.
        for forbidden in ('.value', 'cookie', 'localStorage', 'sessionStorage', 'FormData'):
            self.assertNotIn(forbidden, js, forbidden)

    @override_settings(GOOGLE_SITE_VERIFICATION='abc-token')
    def test_search_console_verification_meta(self):
        self.assertContains(self.client.get(reverse('core:contact')),
                            '<meta name="google-site-verification" content="abc-token">')


@override_settings(CACHES=LOCMEM, LEAD_FORM_THROTTLE='100/3600', LEAD_NOTIFY_EMAIL='', **ADS)
class FormConversionTests(TestCase):
    def setUp(self):
        cache.clear()

    def submit(self, **overrides):
        return self.client.post(reverse('core:enquiry'), {**FORM, **overrides})

    def test_marker_appears_once_after_a_new_lead(self):
        self.submit()
        first = self.client.get(reverse('core:thank_you'))
        self.assertContains(first, 'data-lead-conversion')
        self.assertContains(first, 'data-ads-send-to="AW-123456/formLbl"')
        second = self.client.get(reverse('core:thank_you'))
        self.assertNotContains(second, 'data-lead-conversion')

    def test_refresh_never_double_counts(self):
        self.submit()
        hits = sum('data-lead-conversion' in self.client.get(reverse('core:thank_you')).content.decode()
                   for _ in range(4))
        self.assertEqual(hits, 1)

    def test_no_marker_without_a_submission(self):
        self.assertNotContains(self.client.get(reverse('core:thank_you')), 'data-lead-conversion')

    def test_duplicate_lead_is_saved_but_not_counted(self):
        self.submit()
        self.client.get(reverse('core:thank_you'))
        self.submit()
        self.assertEqual(Lead.objects.count(), 2)
        self.assertNotContains(self.client.get(reverse('core:thank_you')), 'data-lead-conversion')

    def test_honeypot_and_invalid_submissions_are_not_counted(self):
        self.submit(website='http://spam.example')
        self.assertNotContains(self.client.get(reverse('core:thank_you')), 'data-lead-conversion')
        self.submit(phone='12')
        self.assertNotIn(CONVERSION_PENDING, self.client.session)

    def test_marker_carries_no_personal_data(self):
        self.submit()
        html = self.client.get(reverse('core:thank_you')).content.decode()
        marker = html[html.index('<span hidden data-lead-conversion'):]
        marker = marker[:marker.index('</span>')]
        for private in ('Asha', '9876543210', '98765', str(Lead.objects.get().pk) + '"'):
            self.assertNotIn(private, marker)

    @override_settings(GOOGLE_ADS_FORM_CONVERSION_LABEL='')
    def test_marker_without_ads_label_still_reports_the_ga4_event_only(self):
        self.submit()
        html = self.client.get(reverse('core:thank_you')).content.decode()
        self.assertIn('data-lead-conversion', html)
        self.assertNotIn('data-ads-send-to', html)


class CtaTests(TestCase):
    @override_settings(WHATSAPP_NUMBER='919000000000', CONTACT_PHONE='+919000000001', **ADS)
    def test_whatsapp_and_call_links_are_tracked_as_secondary_events(self):
        html = self.client.get(reverse('core:contact')).content.decode()
        self.assertIn('href="https://wa.me/919000000000?text=Hi%2C%20I%20want%20a%20tour%20quote."', html)
        self.assertIn('data-track="whatsapp_click" data-ads-send-to="AW-123456/waLbl"', html)
        self.assertIn('href="tel:+919000000001"', html)
        self.assertIn('data-track="call_click" data-ads-send-to="AW-123456/callLbl"', html)

    @override_settings(WHATSAPP_NUMBER='919000000000', **NO_TAGS)
    def test_links_work_without_tags(self):
        html = self.client.get(reverse('core:contact')).content.decode()
        self.assertIn('https://wa.me/919000000000', html)
        self.assertNotIn('data-ads-send-to', html)

    def test_a_click_is_never_a_lead(self):
        with override_settings(WHATSAPP_NUMBER='919000000000'):
            html = self.client.get(reverse('core:contact')).content.decode()
        self.assertNotIn('data-lead-conversion', html)
        self.assertNotIn('generate_lead', html)
        self.assertEqual(Lead.objects.count(), 0)

    @override_settings(WHATSAPP_NUMBER='', CONTACT_PHONE='')
    def test_nothing_renders_without_numbers_but_quote_link_remains(self):
        html = self.client.get(reverse('core:contact')).content.decode()
        self.assertNotIn('wa.me', html)
        self.assertNotIn('tel:', html)
        self.assertIn('Get free quotes', html)

    @override_settings(WHATSAPP_NUMBER='919000000000', WHATSAPP_PREFILL_TEXT='Hello & welcome 4 people')
    def test_prefill_comes_from_settings_and_is_url_encoded(self):
        html = self.client.get(reverse('core:contact')).content.decode()
        self.assertIn('?text=Hello%20%26%20welcome%204%20people', html)

    def test_prefill_helper_encodes_text(self):
        self.assertEqual(whatsapp_url('9190', 'a b&c'), 'https://wa.me/9190?text=a%20b%26c')

    def test_default_prefill_has_no_personal_details(self):
        from django.conf import settings
        text = settings.WHATSAPP_PREFILL_TEXT
        self.assertFalse(any(ch.isdigit() for ch in text), text)
        self.assertNotIn('@', text)

    @override_settings(WHATSAPP_NUMBER='919000000000')
    def test_sticky_bar_on_content_pages_but_not_on_form_thank_you_or_404(self):
        for name in ('core:contact', 'core:privacy', 'core:terms'):
            self.assertContains(self.client.get(reverse(name)), 'class="sticky-cta"', msg_prefix=name)
        for name in ('core:enquiry', 'core:thank_you'):
            self.assertNotContains(self.client.get(reverse(name)), 'class="sticky-cta"', msg_prefix=name)
        self.assertNotContains(self.client.get('/nope/'), 'class="sticky-cta"', status_code=404)


class StaticAssetsTests(SimpleTestCase):
    def test_tracking_script_exists(self):
        self.assertTrue((STATIC_DIR / 'js' / 'tracking.js').is_file())
