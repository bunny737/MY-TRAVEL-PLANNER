"""Module 08: the Vizag to Araku cab page (a `cab` ContentPage), its cab-specific sections and the cab-ads supply rule."""
import re
from datetime import date
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .admin import CAB_SUPPLY_WARNING
from .models import ContentPage, Lead, Partner
from .test_content import FORBIDDEN_CLAIMS, PRICE_WORDS, make_page, text_of
from .test_partners import make_partner

SLUG = 'vizag-to-araku-cab'


def seed():
    call_command('seed_launch_content', stdout=StringIO())
    return ContentPage.objects.get(slug=SLUG)


def publish(page):
    page.status = 'published'
    page.full_clean()
    page.save()
    return page


@override_settings(SITE_BASE_URL='https://site.test')
class CabPageContentTests(TestCase):
    def test_seed_creates_a_draft_cab_page_that_is_not_public(self):
        page = seed()
        self.assertEqual(page.page_type, 'cab')
        self.assertEqual(page.status, 'draft')
        self.assertIsNone(page.published_at)
        self.assertEqual(page.destination.slug, 'araku-valley')
        self.assertEqual(page.form_service, 'cab')
        self.assertEqual(self.client.get(f'/{SLUG}/').status_code, 404)

    def test_seed_notes_include_the_supply_rule_and_what_to_verify(self):
        notes = seed().internal_notes
        self.assertIn('Before publishing', notes)
        self.assertIn('do NOT start any cab ads', notes)
        self.assertEqual(seed().inclusions, '')  # only operator-confirmed inclusions, added by the owner
        self.assertEqual(seed().exclusions, '')

    def test_published_page_has_cab_sections_not_a_day_by_day_itinerary(self):
        publish(seed())
        html = self.client.get(f'/{SLUG}/').content.decode()
        self.assertIn('Vehicles, pickup points and what to ask', html)
        self.assertNotIn('Example itinerary', html)
        self.assertNotIn('itinerary-timeline', html)
        cards = re.findall(r'<article class="info-card">', html)
        self.assertEqual(len(cards), 5)  # three vehicle groups, pickup points, questions to ask
        for heading in ('Pickup points in Visakhapatnam', 'Questions to ask before you book', 'Tempo travellers'):
            self.assertIn(heading, html)
        self.assertIn('Examples only. The operator who quotes confirms the vehicle, seats and pickup with you.', html)

    def test_cab_wording_replaces_trip_wording(self):
        publish(seed())
        html = self.client.get(f'/{SLUG}/').content.decode()
        self.assertIn('<span>Journey</span>', html)
        self.assertNotIn('<span>Trip length</span>', html)
        self.assertIn('Cab with driver', html)
        self.assertIn('Need a cab from Vizag?', html)
        self.assertNotIn('Ready to plan your trip?', html)
        self.assertIn('Are you the cab operator?', html)

    def test_package_pages_keep_their_itinerary_and_trip_wording(self):
        page = make_page(slug='pkg', title='Pkg', duration='1 day', itinerary='Day 1\nDrive up.')
        html = self.client.get(reverse('core:content_page', args=[page.slug])).content.decode()
        self.assertIn('Example itinerary', html)
        self.assertIn('<span>Trip length</span>', html)
        self.assertIn('Ready to plan your trip?', html)
        self.assertNotIn('info-card', html)

    def test_one_cab_form_with_the_service_preselected_and_the_referral_disclosure(self):
        publish(seed())
        html = self.client.get(f'/{SLUG}/').content.decode()
        self.assertEqual(html.count('<form'), 1)
        self.assertIn('<option value="cab" selected>', html)
        self.assertIn('We are a travel enquiry and referral platform', html)
        self.assertIn('id="quote"', html)

    def test_whatsapp_link_is_prefilled_with_only_the_page_title(self):
        publish(seed())
        with override_settings(WHATSAPP_NUMBER='919000000000'):
            html = self.client.get(f'/{SLUG}/').content.decode()
        self.assertIn('wa.me/919000000000?text=Hi%2C%20I%20want%20a%20quote%20for%20Vizag%20to%20Araku%20Cab.', html)

    def test_no_prices_no_unsourced_numbers_no_overclaims_no_named_operators(self):
        publish(seed())
        text = text_of(self.client.get(f'/{SLUG}/').content.decode()).lower()
        self.assertIsNone(PRICE_WORDS.search(text), PRICE_WORDS.search(text))
        self.assertNotRegex(text, r'\d+\s*(km|kms|hours?|hrs?|seats?|°)', 'distances, durations and seat counts are unsourced')
        for phrase in FORBIDDEN_CLAIMS + ['best cab', 'safest', 'instant', 'cheap']:
            self.assertNotIn(phrase, text, phrase)

    def test_seed_is_valid_to_publish_with_search_fields_within_limits(self):
        page = seed()
        page.status = 'published'
        page.full_clean()
        self.assertLessEqual(len(page.meta_title), 70)
        self.assertLessEqual(len(page.meta_description), 170)
        self.assertEqual(page.hero_key, 'valley-road')

    def test_published_cab_page_is_in_the_sitemap_home_cards_menu_and_has_a_canonical(self):
        publish(seed())
        self.assertIn(f'https://site.test/{SLUG}/', self.client.get('/sitemap.xml').content.decode())
        home = self.client.get('/').content.decode()
        self.assertIn(f'href="/{SLUG}/"', home)
        self.assertIn('<span class="trip-type">Cab</span>', home)
        page_html = self.client.get(f'/{SLUG}/').content.decode()
        self.assertIn(f'<link rel="canonical" href="https://site.test/{SLUG}/">', page_html)
        self.assertIn('BreadcrumbList', page_html)

    def test_a_lead_from_the_cab_page_is_saved_as_a_cab_enquiry(self):
        publish(seed())
        response = self.client.post(reverse('core:enquiry'), {
            'name': 'Asha', 'phone': '98765 43210', 'service_type': 'cab', 'travel_date_or_month': 'November',
            'travellers': '4', 'consent_given': 'on',
        })
        self.assertRedirects(response, reverse('core:thank_you'))
        lead = Lead.objects.get()
        self.assertEqual(lead.service_type, 'cab')
        self.assertEqual(lead.status, 'new')


class CabSupplyTests(TestCase):
    def test_supply_needs_an_active_cab_partner_who_agreed_to_referrals(self):
        self.assertFalse(Partner.cab_supply_confirmed())
        make_partner(business_name='Tours Only', offers_cabs=False, offers_tours=True, referral_terms_agreed_on=date(2026, 10, 25))
        make_partner(business_name='No Terms', phone='98765 43211')
        make_partner(business_name='Inactive', phone='98765 43212', is_active=False, referral_terms_agreed_on=date(2026, 10, 25))
        self.assertFalse(Partner.cab_supply_confirmed())
        make_partner(business_name='Ready Cabs', phone='98765 43213', referral_terms_agreed_on=date(2026, 10, 25))
        self.assertTrue(Partner.cab_supply_confirmed())


class CabAdminWarningTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser('owner', 'o@example.test', 'a-long-test-password-1')

    def setUp(self):
        self.client.force_login(self.owner)

    def warnings(self, response):
        return [m.message for m in get_messages(response.wsgi_request) if CAB_SUPPLY_WARNING == m.message]

    def run_publish_action(self, *pages):
        return self.client.post(reverse('admin:core_contentpage_changelist'), {
            'action': 'publish_pages', '_selected_action': [p.pk for p in pages],
        }, follow=True)

    def test_publishing_a_cab_page_without_a_cab_partner_warns_but_still_publishes(self):
        page = seed()
        response = self.run_publish_action(page)
        page.refresh_from_db()
        self.assertEqual(page.status, 'published')
        self.assertEqual(len(self.warnings(response)), 1)
        self.assertContains(response, 'Do not start cab ads')

    def test_no_warning_once_a_cab_partner_has_agreed(self):
        make_partner(referral_terms_agreed_on=date(2026, 10, 25))
        response = self.run_publish_action(seed())
        self.assertEqual(self.warnings(response), [])

    def test_no_warning_for_package_pages(self):
        response = self.run_publish_action(make_page(slug='pkg', title='Pkg', status='draft'))
        self.assertEqual(self.warnings(response), [])

    def test_saving_a_published_cab_page_in_the_edit_form_warns_too(self):
        page = seed()
        data = {
            'page_type': 'cab', 'title': page.title, 'slug': page.slug, 'status': 'published', 'sort_order': '100',
            'destination': page.destination_id, 'hero_image': 'valley-road', 'intro': page.intro,
            'meta_title': page.meta_title, 'meta_description': page.meta_description,
        }
        response = self.client.post(reverse('admin:core_contentpage_change', args=[page.pk]), data, follow=True)
        self.assertEqual(len(self.warnings(response)), 1, response.content.decode()[:2000])
        page.refresh_from_db()
        self.assertEqual(page.status, 'published')
