"""seed_site_content: every launch draft is publishable, original, price-free, claim-free and honest about the partner."""
import re
from datetime import date
from decimal import Decimal
from io import StringIO

from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from . import images
from .content import format_inr
from .management.commands.seed_site_content import ALL_PAGES
from .models import ContentPage, Destination, Partner
from .seed.prices import PRICES
from .test_content import FORBIDDEN_CLAIMS, PRICE_WORDS, text_of

DISTANCE = re.compile(r'\d+\s*(km|°|degrees)')
PARTNER_MARKS = ('arakutourpackages', 'araku tours & travels', 'araku tours &amp; travels')


def run_seeds():
    out = StringIO()
    call_command('seed_launch_content', stdout=out)
    call_command('seed_site_content', stdout=out)
    return out.getvalue()


class SeedBasicsTests(TestCase):
    def test_creates_every_page_as_a_draft_and_the_two_new_destinations(self):
        run_seeds()
        for item in ALL_PAGES:
            page = ContentPage.objects.get(slug=item['slug'])
            self.assertEqual(page.status, 'draft', item['slug'])
            self.assertIsNone(page.published_at)
        self.assertEqual(Destination.objects.filter(slug__in=['vanjangi', 'maredumilli']).count(), 2)

    def test_covers_every_page_type_and_the_planned_set(self):
        types = {item['fields']['page_type'] for item in ALL_PAGES}
        self.assertEqual(types, {'package', 'cab', 'stay', 'guide', 'article'})
        self.assertGreaterEqual(len([i for i in ALL_PAGES if i['fields']['page_type'] == 'article']), 5)
        self.assertGreaterEqual(len(ALL_PAGES), 30)

    def test_running_twice_creates_nothing_new(self):
        run_seeds()
        count = ContentPage.objects.count()
        out = StringIO()
        call_command('seed_site_content', stdout=out)
        self.assertEqual(ContentPage.objects.count(), count)
        self.assertIn('Created 0 draft page(s)', out.getvalue())

    def test_never_overwrites_a_page_the_owner_has_edited(self):
        run_seeds()
        page = ContentPage.objects.get(slug='araku-honeymoon-package')
        page.intro = 'My own words.'
        page.status = 'published'
        page.save()
        call_command('seed_site_content', stdout=StringIO())
        page.refresh_from_db()
        self.assertEqual(page.intro, 'My own words.')
        self.assertEqual(page.status, 'published')

    def test_never_sets_a_price(self):
        run_seeds()
        self.assertFalse(ContentPage.objects.exclude(price_from=None).exists())
        self.assertFalse(ContentPage.objects.exclude(price_partner=None).exists())

    def test_slugs_and_titles_are_unique_across_both_seeds(self):
        run_seeds()
        pages = list(ContentPage.objects.all())
        for attr in ('slug', 'title', 'effective_title', 'meta_description'):
            values = [getattr(p, attr).casefold() for p in pages]
            self.assertEqual(len(values), len(set(values)), attr)

    def test_photo_keys_exist_and_destinations_are_real(self):
        for item in ALL_PAGES:
            self.assertTrue(images.exists(item['fields']['hero_image']), item['slug'])
        run_seeds()  # raises KeyError on a destination slug that is not created


PRICE_BLOCK = re.compile(r'<!--price-->.*?<!--/price-->', re.S)


@override_settings(PRICE_MAX_AGE_DAYS=100000)  # the quote date is fixed (24 Oct 2026); keep the tests independent of today's date
class PartnerPriceTests(TestCase):
    def setUp(self):
        run_seeds()
        self.partner = Partner.objects.create(business_name='Test Partner', phone='9000000001', offers_tours=True)

    def run_prices(self, **kwargs):
        out = StringIO()
        call_command('set_partner_prices', partner='Test Partner', stdout=out, **kwargs)
        return out.getvalue()

    def test_every_priced_page_gets_its_lowest_option_as_the_from_price_with_partner_and_date(self):
        self.run_prices()
        self.assertEqual(ContentPage.objects.exclude(price_from=None).count(), len(PRICES))
        for slug, unit, basis, _, options in PRICES:
            page = ContentPage.objects.get(slug=slug)
            self.assertEqual(page.price_from, min(amount for _, amount in options), slug)
            self.assertIsInstance(page.price_from, Decimal)
            self.assertEqual(page.price_unit, unit)
            self.assertEqual(page.price_partner, self.partner)
            self.assertEqual(page.price_quoted_on, date(2026, 10, 24))
            self.assertLessEqual(len(basis), 120, slug)
            self.assertEqual(page.status, 'draft')
            page.full_clean()

    def test_option_lists_are_stored_for_pages_with_several_options_only(self):
        self.run_prices()
        for slug, _, _, _, options in PRICES:
            stored = ContentPage.objects.get(slug=slug).price_options
            if len(options) > 1:
                self.assertEqual(stored.splitlines(), [f'{label} | {amount}' for label, amount in options], slug)
            else:
                self.assertEqual(stored, '', slug)

    def test_only_package_and_stay_pages_are_priced_never_cabs_guides_or_articles(self):
        self.run_prices()
        for page in ContentPage.objects.exclude(price_from=None):
            self.assertIn(page.page_type, ('package', 'stay'), page.slug)

    def test_the_four_stay_pages_list_their_properties_per_room_per_night(self):
        self.run_prices()
        stays = ContentPage.objects.filter(page_type='stay')
        self.assertEqual({p.slug for p in stays}, {
            'araku-hotels-and-stays', 'lambasingi-hotels-and-stays', 'vizag-hotels-and-stays', 'maredumilli-hotels-and-stays'})
        for page in stays:
            self.assertEqual(page.price_unit, 'per_room_night', page.slug)
            self.assertEqual(len(page.price_options.splitlines()), 6, page.slug)

    def test_refresh_rewrites_this_partners_prices_but_not_another_partners_or_the_default_run(self):
        self.run_prices()
        page = ContentPage.objects.get(slug='vizag-tour-packages')
        page.price_from = Decimal('1')
        page.save()
        self.run_prices()
        self.assertEqual(ContentPage.objects.get(slug='vizag-tour-packages').price_from, Decimal('1'))  # default never overwrites
        self.run_prices(refresh=True)
        self.assertEqual(ContentPage.objects.get(slug='vizag-tour-packages').price_from, Decimal('6000'))
        other = Partner.objects.create(business_name='Other', phone='9000000002', offers_tours=True)
        ContentPage.objects.filter(slug='vizag-tour-packages').update(price_partner=other, price_from=Decimal('2'))
        self.run_prices(refresh=True)
        self.assertEqual(ContentPage.objects.get(slug='vizag-tour-packages').price_from, Decimal('2'))
        notes = ContentPage.objects.get(slug='vizag-tour-packages').internal_notes
        self.assertEqual(notes.count('PRICE:'), 1)  # the note is added once, not on every refresh

    def test_running_twice_changes_nothing_and_never_overwrites_an_owner_price(self):
        page = ContentPage.objects.get(slug='vizag-to-araku-day-trip')
        page.price_from, page.price_unit, page.price_basis = Decimal('7000'), 'per_couple', 'Owner entered'
        page.price_quoted_on, page.price_partner = date(2026, 10, 25), self.partner
        page.save()
        self.run_prices()
        self.assertEqual(ContentPage.objects.get(slug='vizag-to-araku-day-trip').price_from, Decimal('7000'))
        before = list(ContentPage.objects.values_list('slug', 'price_from', 'internal_notes').order_by('slug'))
        self.assertIn('0 price(s) set', self.run_prices())
        self.assertEqual(before, list(ContentPage.objects.values_list('slug', 'price_from', 'internal_notes').order_by('slug')))

    def test_unknown_partner_is_an_error_and_a_missing_page_is_skipped(self):
        with self.assertRaises(CommandError):
            call_command('set_partner_prices', partner='Nobody', stdout=StringIO())
        ContentPage.objects.filter(slug='maredumilli-tour-package').delete()
        self.assertIn('does not exist', self.run_prices())

    def test_bad_date_is_an_error(self):
        with self.assertRaises(CommandError):
            self.run_prices(quoted_on='24/10/2026')

    def test_notes_say_where_each_price_came_from_and_flag_undated_ones(self):
        self.run_prices()
        for slug, _, _, dated, _ in PRICES:
            notes = ContentPage.objects.get(slug=slug).internal_notes
            self.assertIn('PRICE:', notes, slug)
            self.assertEqual('no date' in notes, not dated, slug)

    def test_published_pages_show_the_from_price_every_option_and_the_date_and_never_name_the_partner(self):
        self.run_prices()
        ContentPage.objects.exclude(page_type='home').update(status='published')
        for slug, _, _, _, options in PRICES:
            html = self.client.get(f'/{slug}/').content.decode()
            blocks = ''.join(PRICE_BLOCK.findall(html))
            self.assertGreaterEqual(len(PRICE_BLOCK.findall(html)), 2, slug)
            self.assertIn(format_inr(min(amount for _, amount in options)), blocks, slug)
            if len(options) > 1:
                for label, amount in options:
                    self.assertIn(label, blocks, slug)
                    self.assertIn(format_inr(amount), blocks, slug)
            self.assertIn('24 Oct 2026', blocks, slug)
            self.assertNotIn('₹', PRICE_BLOCK.sub(' ', html), slug)
            self.assertNotIn('Test Partner', html, slug)

    def test_stay_pages_show_properties_and_rates_but_no_ratings_or_reviews(self):
        self.run_prices()
        ContentPage.objects.exclude(page_type='home').update(status='published')
        for slug in ('araku-hotels-and-stays', 'vizag-hotels-and-stays'):
            text = text_of(self.client.get(f'/{slug}/').content.decode()).lower()
            self.assertIn('per room per night', text, slug)
            self.assertIn('rate', text, slug)
            for banned in ('stars', 'star rating', 'reviews from', 'rated '):
                self.assertNotIn(banned, text, f'{slug}: {banned}')

    def test_pages_that_got_no_price_still_show_none(self):
        self.run_prices()
        ContentPage.objects.exclude(page_type='home').update(status='published')
        for slug in ('cab-service-in-vizag', 'tempo-traveller-and-bus-hire-in-vizag', 'borra-caves-guide', 'araku-in-two-days-from-vizag-sample-plan'):
            self.assertNotIn('₹', self.client.get(f'/{slug}/').content.decode(), slug)

    def test_a_stale_quote_hides_the_headline_and_every_option(self):
        self.run_prices(quoted_on='2020-01-01')
        ContentPage.objects.exclude(page_type='home').update(status='published')
        with override_settings(PRICE_MAX_AGE_DAYS=90):
            html = self.client.get('/araku-honeymoon-package/').content.decode()
            self.assertNotIn('₹', html)
            self.assertEqual(PRICE_BLOCK.findall(html), [])


class SeedContentRulesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        run_seeds()
        # Publishing is the owner's call; here we publish only to check what visitors would see.
        ContentPage.objects.exclude(page_type='home').update(status='published')

    def pages(self):
        return ContentPage.objects.filter(slug__in=[i['slug'] for i in ALL_PAGES])

    def test_every_seeded_page_passes_the_publish_checks(self):
        for page in self.pages():
            page.status = 'published'
            page.full_clean()

    def test_every_seeded_page_renders_one_h1_and_a_self_canonical(self):
        for page in self.pages():
            response = self.client.get(page.get_absolute_url())
            self.assertEqual(response.status_code, 200, page.slug)
            html = response.content.decode()
            self.assertEqual(html.count('<h1'), 1, page.slug)
            self.assertIn(f'<link rel="canonical" href="', html)
            self.assertIn(page.slug, html.split('rel="canonical"')[1].split('>')[0], page.slug)

    def test_no_prices_ratings_overclaims_or_partner_branding_in_any_page(self):
        for page in self.pages():
            html = self.client.get(page.get_absolute_url()).content.decode()
            text = text_of(html).lower()
            self.assertNotIn('₹', html, page.slug)
            self.assertIsNone(PRICE_WORDS.search(text), (page.slug, PRICE_WORDS.search(text)))
            for phrase in FORBIDDEN_CLAIMS:
                self.assertNotIn(phrase, text, f'{page.slug}: {phrase}')
            for mark in PARTNER_MARKS:
                self.assertNotIn(mark, html.lower(), page.slug)
            for banned in ('top rated', 'happy travellers', '24/7', 'no hidden', 'award-winning', 'coldest village'):
                self.assertNotIn(banned, text, f'{page.slug}: {banned}')

    def test_internal_notes_are_never_rendered(self):
        for page in self.pages():
            html = self.client.get(page.get_absolute_url()).content.decode()
            self.assertNotIn('partner-facts-2026-10', html, page.slug)
            self.assertNotIn('VERIFY', html, page.slug)

    def test_distances_appear_only_on_pages_whose_notes_flag_them_for_checking(self):
        for page in self.pages():
            text = text_of(self.client.get(page.get_absolute_url()).content.decode()).lower()
            body_only = text.split('keep exploring')[0]
            if DISTANCE.search(body_only):
                self.assertIn('Figures on this page', page.internal_notes, page.slug)

    def test_every_page_has_the_referral_role_in_plain_words(self):
        for page in self.pages():
            if page.page_type == 'article':
                continue
            text = text_of(self.client.get(page.get_absolute_url()).content.decode()).lower()
            self.assertIn('independent', text, page.slug)

    def test_every_seeded_note_points_to_the_fact_sheet(self):
        for page in self.pages():
            if page.slug in ('araku-tour-packages',):
                continue
            self.assertIn('partner-facts-2026-10', page.internal_notes, page.slug)

    def test_package_cab_and_stay_pages_have_a_form_and_guides_and_articles_do_not(self):
        for page in self.pages():
            html = self.client.get(page.get_absolute_url()).content.decode()
            has_form = 'name="consent_given"' in html
            self.assertEqual(has_form, page.page_type in ('package', 'cab', 'stay'), page.slug)

    def test_listings_menus_blog_and_sitemap_pick_the_pages_up(self):
        packages = self.client.get('/tour-packages/').content.decode()
        for slug in ('vizag-to-araku-day-trip', 'maredumilli-tour-package', 'cab-service-in-vizag', 'araku-hotels-and-stays'):
            self.assertIn(f'href="/{slug}/"', packages, slug)
        blog = self.client.get('/blog/').content.decode()
        self.assertEqual(blog.count('class="post-item"'), 5)
        sitemap = self.client.get('/sitemap.xml').content.decode()
        for item in ALL_PAGES:
            self.assertIn(f'/{item["slug"]}/', sitemap, item['slug'])

    @override_settings(SITE_BASE_URL='https://site.test')
    def test_sitemap_lists_every_page_once(self):
        locs = re.findall(r'<loc>(.*?)</loc>', self.client.get('/sitemap.xml').content.decode())
        self.assertEqual(len(locs), len(set(locs)))
