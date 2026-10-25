"""/tour-packages/, stay pages and the stay enquiry, related pages, nav menus and the homepage trip limit."""
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContentPage, Lead
from .test_content import make_page, text_of
from .test_destinations import make_destination
from .test_leads import LOCMEM, VALID
from .views import HOME_TRIP_LIMIT, RELATED_LIMIT


@override_settings(SITE_BASE_URL='https://site.test')
class TourPackagesPageTests(TestCase):
    def test_lists_published_packages_cabs_and_stays_grouped_by_destination(self):
        araku = make_destination(name='Araku Valley', slug='araku-valley', sort_order=10)
        vizag = make_destination(name='Vizag', slug='vizag', sort_order=20)
        make_page(slug='v1', title='Vizag Trip', destination=vizag)
        make_page(slug='a1', title='Araku Trip', destination=araku)
        make_page(slug='cab1', title='Vizag Cab Page', page_type='cab')
        make_page(slug='stay1', title='Araku Stays Page', page_type='stay')
        make_page(slug='d1', title='Draft Trip', status='draft')
        make_page(slug='g1', title='Some Guide', page_type='guide')
        html = self.client.get('/tour-packages/').content.decode()
        body = html[html.index('<main'):]
        self.assertLess(body.index('Araku Trip'), body.index('Vizag Trip'))
        self.assertIn('id="cabs"', body)
        self.assertIn('id="stays"', body)
        for absent in ('Draft Trip', 'Some Guide'):
            self.assertNotIn(absent, body)

    def test_empty_listing_still_renders_with_a_way_to_ask(self):
        response = self.client.get('/tour-packages/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('href="/enquiry/"', response.content.decode())

    def test_has_one_h1_unique_title_description_canonical_and_the_disclosure(self):
        html = self.client.get('/tour-packages/').content.decode()
        self.assertEqual(html.count('<h1'), 1)
        self.assertRegex(html, r'<title>[^<]+</title>')
        self.assertRegex(html, r'<meta name="description" content="[^"]{40,}')
        self.assertIn('<link rel="canonical" href="https://site.test/tour-packages/">', html)
        self.assertIn('referral-disclosure', html)

    def test_is_indexable_and_in_the_sitemap(self):
        self.assertIn('content="index,follow"', self.client.get('/tour-packages/').content.decode())
        self.assertIn('https://site.test/tour-packages/', self.client.get('/sitemap.xml').content.decode())


class HomepageTripTests(TestCase):
    def test_homepage_shows_at_most_the_limit_and_links_to_the_full_list(self):
        for i in range(HOME_TRIP_LIMIT + 2):
            make_page(slug=f'trip-{i}', title=f'Trip Number {i}', sort_order=i)
        html = self.client.get('/').content.decode()
        section = html[html.index('Trips you can ask about'):]
        self.assertEqual(section.count('class="trip-card"'), HOME_TRIP_LIMIT)
        self.assertIn('See all tour packages, cabs and stays', html)

    def test_stay_pages_are_listed_on_the_homepage(self):
        make_page(slug='stay-one', title='Stay One', page_type='stay')
        html = self.client.get('/').content.decode()
        self.assertIn('href="/stay-one/"', html[html.index('Trips you can ask about'):])


class NavMenuTests(TestCase):
    def nav(self):
        html = self.client.get('/').content.decode()
        return html[html.index('<header class="site-header">'):html.index('</header>')]

    def test_menus_list_published_pages_only_and_hide_when_empty(self):
        nav = self.nav()
        self.assertNotIn('Tour packages</summary>', nav)
        self.assertNotIn('Cabs &amp; stays</summary>', nav)
        make_page(slug='p1', title='Live Package')
        make_page(slug='p2', title='Draft Package', status='draft')
        make_page(slug='c1', title='Live Cab', page_type='cab')
        make_page(slug='s1', title='Live Stay', page_type='stay')
        nav = self.nav()
        self.assertIn('Tour packages</summary>', nav)
        self.assertIn('href="/p1/"', nav)
        self.assertNotIn('Draft Package', nav)
        self.assertIn('href="/c1/"', nav)
        self.assertIn('href="/s1/"', nav)
        self.assertIn('href="/tour-packages/"', nav)

    def test_blog_is_in_the_nav_and_footer_and_menus_need_no_javascript(self):
        html = self.client.get('/').content.decode()
        self.assertIn('href="/blog/"', html[html.index('<header'):html.index('</header>')])
        self.assertIn('href="/blog/"', html[html.index('<footer'):])
        self.assertNotIn('<script', self.nav())


class RelatedPagesTests(TestCase):
    def test_related_pages_are_published_same_destination_and_not_the_page_itself(self):
        araku = make_destination(name='Araku Valley', slug='araku-valley')
        vizag = make_destination(name='Vizag', slug='vizag')
        main = make_page(slug='main', title='Main Page', destination=araku)
        make_page(slug='sib', title='Sibling Trip', destination=araku)
        make_page(slug='sib-draft', title='Draft Sibling', destination=araku, status='draft')
        make_page(slug='other', title='Other Place Trip', destination=vizag)
        html = self.client.get(main.get_absolute_url()).content.decode()
        related = html[html.index('related-list'):]
        self.assertIn('Sibling Trip', related)
        for absent in ('Draft Sibling', 'Other Place Trip', 'Main Page'):
            self.assertNotIn(absent, related)

    def test_commercial_pages_come_before_guides_and_the_list_is_capped(self):
        araku = make_destination(name='Araku Valley', slug='araku-valley')
        main = make_page(slug='main', title='Main Guide', page_type='guide', destination=araku)
        make_page(slug='the-guide', title='Another Guide Page', page_type='guide', destination=araku, sort_order=1)
        make_page(slug='the-package', title='The Package Page', destination=araku, sort_order=99)
        html = self.client.get(main.get_absolute_url()).content.decode()
        related = html[html.index('related-list'):]
        self.assertLess(related.index('The Package Page'), related.index('Another Guide Page'))
        for i in range(RELATED_LIMIT + 3):
            make_page(slug=f'x{i}', title=f'Extra {i}', destination=araku)
        related = self.client.get(main.get_absolute_url()).content.decode().split('related-list')[1]
        self.assertEqual(related.count('class="related-item"'), RELATED_LIMIT)

    def test_pages_without_a_destination_show_no_related_section(self):
        page = make_page(slug='solo', title='Solo Page')
        make_page(slug='other', title='Other Page')
        self.assertNotIn('related-list', self.client.get(page.get_absolute_url()).content.decode())


@override_settings(CACHES=LOCMEM, LEAD_FORM_THROTTLE='100/3600', LEAD_NOTIFY_EMAIL='')
class StayPageAndLeadTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_a_stay_page_has_the_form_with_stay_preselected(self):
        make_page(slug='stays', title='Stays in Araku', page_type='stay')
        html = self.client.get('/stays/').content.decode()
        self.assertIn('name="consent_given"', html)
        self.assertRegex(html, r'<option value="stay"[^>]*selected')
        self.assertEqual(ContentPage.objects.get(slug='stays').form_service, 'stay')

    def test_the_stay_option_is_offered_on_the_enquiry_page(self):
        html = self.client.get(reverse('core:enquiry')).content.decode()
        self.assertIn('<option value="stay"', html)

    def test_a_stay_enquiry_is_saved_with_consent_like_any_other_lead(self):
        response = self.client.post(reverse('core:enquiry'), {**VALID, 'service_type': 'stay'})
        self.assertRedirects(response, reverse('core:thank_you'))
        lead = Lead.objects.get()
        self.assertEqual(lead.service_type, 'stay')
        self.assertTrue(lead.consent_given)
        self.assertEqual(lead.consent_source, Lead.ConsentSource.FORM)

    def test_a_stay_enquiry_without_consent_is_refused(self):
        data = {k: v for k, v in VALID.items() if k != 'consent_given'}
        response = self.client.post(reverse('core:enquiry'), {**data, 'service_type': 'stay'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)

    def test_stay_pages_state_the_referral_role_and_no_overclaims(self):
        make_page(slug='stays', title='Stays in Araku', page_type='stay')
        text = text_of(self.client.get('/stays/').content.decode()).lower()
        self.assertIn('referral platform', text)
        for word in ('cheapest', 'guaranteed', 'instant confirmation', '5-star'):
            self.assertNotIn(word, text)
