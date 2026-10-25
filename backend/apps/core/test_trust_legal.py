import re

from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.urls import reverse

PAGES = ['core:contact', 'core:privacy', 'core:terms']

DISCLOSURE = (
    'We are a travel enquiry and referral platform. With your permission, we will share your trip '
    'requirements and contact details with selected independent travel partners so they can contact '
    'you with quotes. Bookings and tour delivery are handled by those partners.'
)

# Wording pinned on purpose: if you change partials/consent_notice.html you MUST bump CONSENT_NOTICE_VERSION
# and update this constant in the same commit (CLAUDE.md invariant 1).
CONSENT_TEXT_V1 = (
    'I agree that Test Brand may share my name, phone number and trip details with one selected '
    'independent travel partner so they can contact me with quotes. We will ask before sharing with '
    'anyone else. See our Privacy Policy.'
)
CONSENT_VERSION_FOR_TEXT = '2026-10-v1'

# Words that would breach CLAUDE.md invariant 3 (honest claims) if used as a promise on these pages.
FORBIDDEN_CLAIMS = ['cheapest', 'guaranteed', 'instant confirmation', 'verified', 'best price', '5-star', 'official tourism']


def visible_text(html):
    html = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S)
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()
    return re.sub(r'\s+([.,])', r'\1', text)  # tag removal leaves a gap before punctuation


@override_settings(SITE_NAME='Test Brand')
class TrustPagesTests(TestCase):
    def test_pages_render_indexable_with_unique_title_and_meta(self):
        titles, metas = set(), set()
        for name in PAGES:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)
            html = response.content.decode()
            self.assertIn('content="index,follow"', html, name)
            self.assertIn(f'<link rel="canonical" href="http://localhost:8100{reverse(name)}">', html, name)
            self.assertIn('<h1>', html, name)
            title = re.search(r'<title>(.*?)</title>', html).group(1)
            meta = re.search(r'name="description" content="(.*?)"', html).group(1)
            self.assertTrue(title and meta, name)
            titles.add(title)
            metas.add(meta)
        self.assertEqual(len(titles), len(PAGES))
        self.assertEqual(len(metas), len(PAGES))

    def test_referral_disclosure_wording_on_contact_and_terms(self):
        for name in ('core:contact', 'core:terms'):
            text = visible_text(self.client.get(reverse(name)).content.decode())
            self.assertIn(DISCLOSURE, text, name)

    def test_disclosure_partial_is_exact_plan_wording(self):
        self.assertIn(DISCLOSURE, visible_text(render_to_string('partials/referral_disclosure.html')))

    def test_footer_links_to_legal_pages_on_every_page(self):
        for name in PAGES:
            html = self.client.get(reverse(name)).content.decode()
            for target in PAGES:
                self.assertIn(f'href="{reverse(target)}"', html, f'{name} -> {target}')

    def test_no_promotional_claims_on_legal_pages(self):
        for name in PAGES:
            text = visible_text(self.client.get(reverse(name)).content.decode()).lower()
            for phrase in FORBIDDEN_CLAIMS:
                self.assertNotIn(phrase, text, f'{name}: {phrase}')

    def test_terms_state_referral_only_role(self):
        text = visible_text(self.client.get(reverse('core:terms')).content.decode())
        self.assertIn('not a tour operator', text)
        self.assertIn('We do not take payment for your trip', text)
        self.assertIn('independent businesses', text)

    def test_privacy_covers_sharing_with_one_partner_and_withdrawal(self):
        text = visible_text(self.client.get(reverse('core:privacy')).content.decode())
        self.assertIn('one selected independent partner', text)
        self.assertIn('ask you again before sharing with any other partner', text)
        self.assertIn('withdraw your consent', text)
        self.assertIn('do not sell your personal data', text)
        self.assertIn('do not put your name, phone number or enquiry details into these tools', text)


class ContactPageTests(TestCase):
    @override_settings(CONTACT_EMAIL='', CONTACT_PHONE='', WHATSAPP_NUMBER='', RESPONSE_HOURS_TEXT='')
    def test_blank_config_renders_no_contact_lines_or_hours(self):
        html = self.client.get(reverse('core:contact')).content.decode()
        self.assertNotIn('mailto:', html)
        self.assertNotIn('tel:', html)
        self.assertNotIn('wa.me', html)
        self.assertNotIn('When we reply', html)

    @override_settings(CONTACT_EMAIL='hello@example.test', CONTACT_PHONE='+919000000000',
                       WHATSAPP_NUMBER='919000000000', RESPONSE_HOURS_TEXT='Weekdays 7-9 AM IST')
    def test_configured_contact_details_and_hours_are_shown(self):
        html = self.client.get(reverse('core:contact')).content.decode()
        self.assertIn('mailto:hello@example.test', html)
        self.assertIn('tel:+919000000000', html)
        self.assertIn('https://wa.me/919000000000', html)
        self.assertIn('Weekdays 7-9 AM IST', html)

    @override_settings(CONTACT_EMAIL='hello@example.test')
    def test_privacy_shows_withdrawal_email_when_configured(self):
        self.assertContains(self.client.get(reverse('core:privacy')), 'mailto:hello@example.test')


@override_settings(SITE_NAME='Test Brand')
class ConsentNoticeTests(TestCase):
    def test_consent_wording_matches_pinned_text_for_current_version(self):
        text = visible_text(render_to_string('partials/consent_notice.html', {'site': {'name': 'Test Brand'}}))
        self.assertEqual(text, CONSENT_TEXT_V1)

    def test_consent_version_is_the_one_the_text_was_pinned_for(self):
        from django.conf import settings
        self.assertEqual(settings.CONSENT_NOTICE_VERSION, CONSENT_VERSION_FOR_TEXT)
