"""Destinations: menu, /destinations/ hub, homepage cards, seed content (Araku Valley, Lambasingi, Vizag)."""
import re
import xml.etree.ElementTree as ET
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from . import images
from .models import ContentPage, Destination
from .test_content import FORBIDDEN_CLAIMS, PRICE_WORDS, make_page, text_of


def make_destination(**overrides):
    n = Destination.objects.count() + 1
    data = dict(name=f'Place {n}', slug=f'place-{n}', summary=f'Summary {n}.', sort_order=n * 10)
    data.update(overrides)
    return Destination.objects.create(**data)


def nav_of(html):
    return html[html.index('<header class="site-header">'):html.index('</header>')]


def footer_of(html):
    return html[html.index('<footer'):]


class DestinationModelTests(TestCase):
    def test_unknown_photo_is_refused_and_library_photos_are_accepted(self):
        with self.assertRaises(ValidationError) as ctx:
            Destination(name='X', slug='x', hero_image='nope').full_clean()
        self.assertIn('hero_image', ctx.exception.message_dict)
        Destination(name='Y', slug='y', hero_image='lambasingi-valley').full_clean()

    def test_hero_key_falls_back_to_the_default_photo(self):
        self.assertEqual(Destination(name='Z', slug='z').hero_key, images.DEFAULT_HERO)
        self.assertEqual(Destination(name='Z', slug='z', hero_image='kailasagiri-coast').hero_key, 'kailasagiri-coast')

    def test_destinations_slug_is_reserved(self):
        with self.assertRaises(ValidationError):
            ContentPage(page_type='guide', title='D', slug='destinations').full_clean()


class MenuTests(TestCase):
    def test_menu_lists_active_destinations_in_order_and_hides_inactive(self):
        make_destination(name='Vizag', slug='vizag', sort_order=30)
        make_destination(name='Araku Valley', slug='araku-valley', sort_order=10)
        make_destination(name='Hidden Place', slug='hidden', is_active=False)
        nav = nav_of(self.client.get(reverse('core:contact')).content.decode())
        self.assertIn('Destinations', nav)
        self.assertLess(nav.index('Araku Valley'), nav.index('Vizag'))
        self.assertNotIn('Hidden Place', nav)
        self.assertIn(f'href="{reverse("core:destinations")}"', nav)

    def test_draft_pages_are_never_linked_the_menu_falls_back_to_the_hub(self):
        place = make_destination(name='Lambasingi', slug='lambasingi')
        make_page(slug='lambasingi-tour-packages', title='Lambasingi Tours', destination=place, status='draft')
        html = self.client.get(reverse('core:contact')).content.decode()
        self.assertNotIn('/lambasingi-tour-packages/', html)
        self.assertIn('href="/destinations/#lambasingi"', nav_of(html))

    def test_published_page_becomes_the_menu_link_package_before_cab_and_guide(self):
        place = make_destination(name='Vizag', slug='vizag')
        make_page(slug='vizag-guide', title='Vizag Guide', page_type='guide', destination=place)
        make_page(slug='vizag-cab', title='Vizag Cab', page_type='cab', destination=place)
        nav = nav_of(self.client.get(reverse('core:contact')).content.decode())
        self.assertIn('href="/vizag-cab/"', nav)
        make_page(slug='vizag-tours', title='Vizag Tours', destination=place)
        nav = nav_of(self.client.get(reverse('core:contact')).content.decode())
        self.assertIn('href="/vizag-tours/"', nav)
        self.assertNotIn('href="/vizag-cab/"', nav)

    def test_footer_lists_destinations_and_nothing_says_araku_packages_only(self):
        make_destination(name='Lambasingi', slug='lambasingi')
        html = self.client.get('/').content.decode()
        footer = footer_of(html)
        self.assertIn('Lambasingi', footer)
        self.assertIn('All destinations', footer)
        self.assertNotIn('Araku Packages', html)
        self.assertNotIn('Araku Tour Packages</a>', footer)
        self.assertIn('Lambasingi, Vizag', footer)  # tagline names the whole region

    def test_menu_needs_no_javascript(self):
        nav = nav_of(self.client.get('/').content.decode())
        self.assertIn('<details class="nav-dropdown">', nav)
        self.assertNotIn('<script', nav)


@override_settings(SITE_BASE_URL='https://site.test')
class HubPageTests(TestCase):
    def setUp(self):
        self.araku = make_destination(name='Araku Valley', slug='araku-valley', hero_image='rainbow-hills', sort_order=10)
        self.lambasingi = make_destination(name='Lambasingi', slug='lambasingi', hero_image='lambasingi-valley',
                                           sort_order=20)
        make_page(slug='araku-tours', title='Araku Tours', destination=self.araku)
        make_page(slug='lambasingi-draft', title='Lambasingi Draft', destination=self.lambasingi, status='draft')

    def test_hub_lists_each_destination_with_photo_and_the_right_action(self):
        response = self.client.get(reverse('core:destinations'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertEqual(html.count('<h1>'), 1)
        self.assertEqual(html.count('class="destination-card"'), 2)
        self.assertIn('id="araku-valley"', html)
        self.assertIn('rainbow-hills-800.webp', html)
        self.assertIn('lambasingi-valley-800.webp', html)
        araku = html[html.index('id="araku-valley"'):html.index('id="lambasingi"')]
        self.assertIn('href="/araku-tours/"', araku)
        self.assertIn('View trips', araku)
        lambasingi = html[html.index('id="lambasingi"'):]
        self.assertIn('Ask for a free quote', lambasingi)
        self.assertIn(f'href="{reverse("core:enquiry")}"', lambasingi)
        self.assertNotIn('lambasingi-draft', html)

    def test_hub_is_indexable_canonical_and_in_the_sitemap(self):
        html = self.client.get(reverse('core:destinations')).content.decode()
        self.assertIn('content="index,follow"', html)
        self.assertIn('<link rel="canonical" href="https://site.test/destinations/">', html)
        root = ET.fromstring(self.client.get('/sitemap.xml').content)
        locs = [el.text for el in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertIn('https://site.test/destinations/', locs)

    def test_hub_title_and_description_are_unique(self):
        hub = self.client.get(reverse('core:destinations')).content.decode()
        home = self.client.get('/').content.decode()
        title = re.search(r'<title>(.*?)</title>', hub).group(1)
        self.assertNotEqual(title, re.search(r'<title>(.*?)</title>', home).group(1))
        self.assertIn('Destinations', title)
        self.assertRegex(hub, r'<meta name="description" content="[^"]{50,}">')

    def test_hub_has_disclosure_and_no_prices_or_overclaims(self):
        html = self.client.get(reverse('core:destinations')).content.decode()
        self.assertIn('We are a travel enquiry and referral platform', html)
        text = text_of(html).lower()
        self.assertIsNone(PRICE_WORDS.search(text))
        for phrase in FORBIDDEN_CLAIMS:
            self.assertNotIn(phrase, text, phrase)

    def test_homepage_shows_the_same_cards_and_links_to_the_hub(self):
        html = self.client.get('/').content.decode()
        band = html[html.index('destinations-section'):html.index('explore-section')]
        self.assertIn('Where would you like to go?', band)
        self.assertEqual(band.count('class="destination-card"'), 2)
        self.assertIn(f'href="{reverse("core:destinations")}"', band)

    def test_homepage_copy_names_the_whole_region(self):
        html = self.client.get('/').content.decode()
        hero = html[html.index('home-hero'):html.index('promise-wrap')]
        for place in ('Vizag', 'Araku', 'Lambasingi'):
            self.assertIn(place, hero, place)


class PageGalleryByPlaceTests(TestCase):
    def test_gallery_shows_only_photos_of_the_page_destination(self):
        vizag = make_destination(name='Vizag', slug='vizag')
        page = make_page(slug='vizag-tours', title='Vizag Tours', destination=vizag, hero_image='valley-dusk')
        html = self.client.get(reverse('core:content_page', args=[page.slug])).content.decode()
        gallery = html[html.index('gallery-grid'):]
        self.assertIn('rushikonda-beach', gallery)
        self.assertIn('kailasagiri-coast', gallery)
        self.assertNotIn('borra-caves', gallery)

    def test_no_gallery_when_the_destination_has_fewer_than_two_other_photos(self):
        lambasingi = make_destination(name='Lambasingi', slug='lambasingi')
        page = make_page(slug='lam', title='Lam', destination=lambasingi, hero_image='lambasingi-clouds')
        html = self.client.get(reverse('core:content_page', args=[page.slug])).content.decode()
        self.assertNotIn('gallery-grid', html)

    def test_page_hero_pill_names_its_destination(self):
        lambasingi = make_destination(name='Lambasingi', slug='lambasingi')
        page = make_page(slug='lam', title='Lam', destination=lambasingi)
        html = self.client.get(reverse('core:content_page', args=[page.slug])).content.decode()
        self.assertIn('<span class="hero-pill">Lambasingi</span>', html)


class SeedDestinationsTests(TestCase):
    def run_seed(self):
        out = StringIO()
        call_command('seed_launch_content', stdout=out)
        return out.getvalue()

    def test_creates_three_destinations_with_photos_and_three_drafts(self):
        self.run_seed()
        self.assertEqual(list(Destination.objects.values_list('slug', flat=True)), ['araku-valley', 'lambasingi', 'vizag'])
        for destination in Destination.objects.all():
            destination.full_clean()
            self.assertTrue(destination.hero_image and destination.summary, destination.slug)
        for slug, place in (('lambasingi-tour-packages', 'lambasingi'), ('vizag-tour-packages', 'vizag')):
            page = ContentPage.objects.get(slug=slug)
            self.assertEqual(page.status, 'draft', slug)
            self.assertEqual(page.destination.slug, place, slug)
            self.assertIn('Before publishing', page.internal_notes, slug)
            self.assertEqual(page.inclusions, '', slug)
            self.assertEqual(self.client.get(f'/{slug}/').status_code, 404, slug)

    def test_new_drafts_are_publishable_without_prices_or_overclaims(self):
        self.run_seed()
        for slug in ('lambasingi-tour-packages', 'vizag-tour-packages'):
            page = ContentPage.objects.get(slug=slug)
            page.status = 'published'
            page.full_clean()
            page.save()
            text = text_of(self.client.get(f'/{slug}/').content.decode()).lower()
            self.assertIsNone(PRICE_WORDS.search(text), slug)
            self.assertNotRegex(text, r'\d+\s*(km|°|degrees)', slug)  # no unsourced distances or temperatures
            for phrase in FORBIDDEN_CLAIMS:
                self.assertNotIn(phrase, text, f'{slug}: {phrase}')

    def test_rerun_fills_only_blank_destination_fields_and_keeps_edits(self):
        Destination.objects.create(name='Araku', slug='araku-valley', summary='My own words.')
        self.run_seed()
        araku = Destination.objects.get(slug='araku-valley')
        self.assertEqual(araku.summary, 'My own words.')
        self.assertEqual(araku.name, 'Araku')
        self.assertEqual(araku.hero_image, 'rainbow-hills')  # was blank, so filled
        self.assertEqual(araku.sort_order, 10)  # was the default, so set; a chosen order would be kept
        Destination.objects.filter(slug='vizag').update(sort_order=5)
        self.run_seed()
        self.assertEqual(Destination.objects.get(slug='vizag').sort_order, 5)
        self.assertIn('already exists', self.run_seed())
        self.assertEqual(Destination.objects.count(), 3)
        self.assertEqual(ContentPage.objects.count(), 4)  # three package drafts and the cab draft

    def test_seeded_menu_points_at_the_hub_until_pages_are_published(self):
        self.run_seed()
        nav = nav_of(self.client.get('/').content.decode())
        for slug in ('araku-valley', 'lambasingi', 'vizag'):
            self.assertIn(f'href="/destinations/#{slug}"', nav)
        ContentPage.objects.filter(slug='lambasingi-tour-packages').update(status='published')
        nav = nav_of(self.client.get('/').content.decode())
        self.assertIn('href="/lambasingi-tour-packages/"', nav)
