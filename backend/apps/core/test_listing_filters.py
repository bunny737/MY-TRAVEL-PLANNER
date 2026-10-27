"""/tour-packages/ filters (type, place, trip length), sort, and the days_min / days_max fields behind them."""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from .models import ContentPage
from .seed.packages import PACKAGES
from .test_content import make_page, text_of
from .test_destinations import make_destination
from .test_prices import priced_page

ALL_TITLES = ('One Day Trip', 'Two Day Trip', 'Long Trip', 'Flexible Trip', 'Undated Trip', 'Cab One', 'Stay One')


@override_settings(SITE_BASE_URL='https://site.test')
class ListingFilterTests(TestCase):
    def setUp(self):
        self.araku = make_destination(name='Araku Valley', slug='araku-valley', sort_order=10)
        self.vizag = make_destination(name='Vizag City', slug='vizag-city', sort_order=20)
        make_page(slug='one-day', title='One Day Trip', destination=self.araku, days_min=1, days_max=1, sort_order=30)
        make_page(slug='two-day', title='Two Day Trip', destination=self.araku, days_min=2, days_max=2, sort_order=20)
        make_page(slug='long-trip', title='Long Trip', destination=self.vizag, days_min=4, days_max=5, sort_order=10)
        make_page(slug='any-trip', title='Flexible Trip', destination=self.vizag, days_min=1, days_max=5, sort_order=40)
        make_page(slug='no-days', title='Undated Trip', destination=self.vizag, sort_order=50)
        make_page(slug='cab-one', title='Cab One', page_type='cab', destination=self.araku)
        make_page(slug='stay-one', title='Stay One', page_type='stay', destination=self.vizag)
        make_page(slug='draft-trip', title='Draft Trip', days_min=2, days_max=2, status='draft')

    def body(self, query=''):
        response = self.client.get('/tour-packages/' + query)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        return html[html.index('<main'):]

    def titles(self, query='', among=ALL_TITLES):
        """The trip titles shown, in page order."""
        body = self.body(query)
        return sorted((t for t in among if t in body), key=body.index)

    def test_unfiltered_page_shows_everything_published_and_no_drafts(self):
        self.assertEqual(len(self.titles()), 7)
        self.assertNotIn('Draft Trip', self.body())

    def test_type_tab_shows_only_that_type(self):
        self.assertEqual(self.titles('?type=cab'), ['Cab One'])
        self.assertEqual(self.titles('?type=stay'), ['Stay One'])
        self.assertEqual(set(self.titles('?type=package')), set(ALL_TITLES) - {'Cab One', 'Stay One'})

    def test_destination_filter_applies_to_every_type(self):
        self.assertEqual(set(self.titles('?destination=araku-valley')), {'One Day Trip', 'Two Day Trip', 'Cab One'})

    def test_trip_length_matches_overlapping_ranges_and_leaves_out_cabs_and_stays(self):
        self.assertEqual(set(self.titles('?days=1')), {'One Day Trip', 'Flexible Trip'})
        self.assertEqual(set(self.titles('?days=2')), {'Two Day Trip', 'Flexible Trip'})
        self.assertEqual(set(self.titles('?days=3')), {'Flexible Trip'})
        self.assertEqual(set(self.titles('?days=4')), {'Long Trip', 'Flexible Trip'})

    def test_filters_combine(self):
        self.assertEqual(set(self.titles('?days=4&destination=vizag-city')), {'Long Trip', 'Flexible Trip'})
        self.assertEqual(self.titles('?days=4&destination=araku-valley'), [])

    def test_unknown_values_are_ignored(self):
        self.assertEqual(len(self.titles('?type=zzz&destination=nope&days=99&sort=drop')), 7)

    def test_drafts_never_appear_under_any_filter(self):
        for query in ('?days=2', '?type=package', '?sort=shortest', '?sort=price'):
            self.assertNotIn('Draft Trip', self.body(query), query)

    def test_recommended_sort_groups_packages_by_destination_in_admin_order(self):
        body = self.body('?type=package')
        self.assertIn('Araku Valley</h2>', body)
        self.assertLess(body.index('Araku Valley</h2>'), body.index('Vizag City</h2>'))
        self.assertLess(body.index('Two Day Trip'), body.index('One Day Trip'))  # sort_order 20 before 30
        self.assertLess(body.index('Long Trip'), body.index('Flexible Trip'))

    def test_shortest_sort_is_one_flat_list_with_unset_lengths_last(self):
        query = '?sort=shortest&type=package'
        self.assertEqual(
            self.titles(query), ['One Day Trip', 'Flexible Trip', 'Two Day Trip', 'Long Trip', 'Undated Trip'],
        )
        self.assertNotIn('Araku Valley</h2>', self.body(query))

    def test_price_sort_ranks_current_prices_only_and_puts_the_rest_last(self):
        priced_page(slug='dear', title='Dear Trip', days_min=2, days_max=2, price_from=Decimal('9000'), sort_order=1)
        priced_page(slug='low', title='Low Trip', days_min=2, days_max=2, price_from=Decimal('4000'), sort_order=2)
        priced_page(slug='stale', title='Stale Trip', days_min=2, days_max=2, price_from=Decimal('100'),
                    days_ago=200, sort_order=3)
        among = ('Dear Trip', 'Low Trip', 'Stale Trip', 'One Day Trip')
        self.assertEqual(
            self.titles('?sort=price&type=package', among=among), ['Low Trip', 'Dear Trip', 'Stale Trip', 'One Day Trip'],
        )
        self.assertNotIn('₹100', self.body('?sort=price'))  # the expired price stays hidden
        self.assertIn('current dated partner quote', self.body('?sort=price'))

    def test_filtered_urls_keep_the_plain_canonical_and_stay_indexable(self):
        html = self.client.get('/tour-packages/?days=2&sort=price').content.decode()
        self.assertIn('<link rel="canonical" href="https://site.test/tour-packages/">', html)
        self.assertIn('content="index,follow"', html)
        self.assertNotIn('/tour-packages/?', self.client.get('/sitemap.xml').content.decode())

    def test_links_keep_the_other_filters_and_drop_defaults(self):
        body = self.body('?destination=vizag-city&sort=shortest')
        self.assertIn('href="/tour-packages/?destination=vizag-city&amp;days=2&amp;sort=shortest"', body)  # trip-length chip
        self.assertIn('href="/tour-packages/?sort=shortest"', body)  # "All places"
        self.assertIn('Clear filters', body)
        self.assertNotIn('type=all', body)
        self.assertNotIn('sort=recommended', body)

    def test_an_empty_result_explains_itself_and_offers_a_way_to_ask(self):
        html = self.client.get('/tour-packages/?days=4&destination=araku-valley').content.decode()
        self.assertIn('No trips match these filters', html)
        self.assertIn("Can't find the trip you want?", html)
        self.assertIn('href="/enquiry/"', html)

    def test_the_listing_makes_no_overclaims_and_shows_no_rupee_without_a_price(self):
        for query in ('', '?sort=price', '?days=2'):
            text = text_of(self.client.get('/tour-packages/' + query).content.decode()).lower()
            for phrase in ('cheapest', 'guaranteed', 'instant confirmation', 'best price', 'best deal', 'official', '₹'):
                self.assertNotIn(phrase, text, f'{phrase} on {query}')

    def test_the_sort_form_sends_only_filter_values(self):
        html = self.client.get('/tour-packages/?days=2&destination=araku-valley').content.decode()
        form = html[html.index('class="listing-sort"'):]
        form = form[:form.index('</form>')]
        self.assertIn('method="get"', html[html.index('class="listing-sort"') - 60:])
        for name in ('destination', 'days', 'sort'):  # a default (type=all) is left out
            self.assertIn(f'name="{name}"', form)
        self.assertNotIn('csrfmiddlewaretoken', form)


class TripLengthFieldTests(TestCase):
    def check(self, page_type='package', **fields):
        ContentPage(page_type=page_type, title='T', slug='t', **fields).full_clean()

    def test_both_or_neither_is_required(self):
        self.check()
        self.check(days_min=2, days_max=3)
        for fields in ({'days_min': 2}, {'days_max': 2}):
            with self.assertRaises(ValidationError, msg=fields):
                self.check(**fields)

    def test_range_must_be_sensible(self):
        for fields in ({'days_min': 0, 'days_max': 2}, {'days_min': 5, 'days_max': 2}):
            with self.assertRaises(ValidationError, msg=fields):
                self.check(**fields)

    def test_only_packages_have_a_length_in_days(self):
        for page_type in ('cab', 'stay', 'guide', 'article'):
            with self.assertRaises(ValidationError, msg=page_type):
                self.check(page_type=page_type, days_min=1, days_max=1)

    def test_every_seeded_launch_package_carries_a_length(self):
        for item in PACKAGES:
            fields = item['fields']
            self.assertIsNotNone(fields['days_min'], item['slug'])
            self.assertLessEqual(fields['days_min'], fields['days_max'], item['slug'])


class BackfillMigrationTests(TestCase):
    """Migration 0008 fills the launch packages already in the database, and never overwrites a value set in admin."""

    def run_backfill(self):
        from importlib import import_module

        from django.apps import apps
        import_module('apps.core.migrations.0008_contentpage_days').fill_launch_package_days(apps, None)

    def test_fills_empty_launch_packages_only(self):
        empty = make_page(slug='araku-2-days-1-night-tour-package')
        edited = make_page(slug='vizag-to-araku-day-trip', days_min=1, days_max=2)
        other = make_page(slug='some-other-package')
        self.run_backfill()
        for page in (empty, edited, other):
            page.refresh_from_db()
        self.assertEqual((empty.days_min, empty.days_max), (2, 2))
        self.assertEqual((edited.days_min, edited.days_max), (1, 2))
        self.assertEqual((other.days_min, other.days_max), (None, None))

    def test_the_backfill_table_matches_the_seed(self):
        from importlib import import_module
        table = import_module('apps.core.migrations.0008_contentpage_days').LAUNCH_PACKAGE_DAYS
        self.assertEqual(table, {item['slug']: (item['fields']['days_min'], item['fields']['days_max']) for item in PACKAGES})


class TypeTabAvailabilityTests(TestCase):
    def test_tabs_only_for_types_that_have_published_pages(self):
        make_page(slug='p1', title='Package One')
        make_page(slug='s1', title='Stay One', page_type='stay')
        make_page(slug='c1', title='Draft Cab', page_type='cab', status='draft')
        html = self.client.get('/tour-packages/').content.decode()
        self.assertIn('aria-label="Filter by type"', html)
        self.assertIn('>Stays</a>', html)
        self.assertNotIn('>Cabs</a>', html)

    def test_a_type_without_pages_is_ignored_and_one_type_alone_shows_no_tabs(self):
        make_page(slug='p1', title='Package One')
        html = self.client.get('/tour-packages/?type=cab').content.decode()
        self.assertIn('Package One', html)
        self.assertNotIn('aria-label="Filter by type"', html)


class MultiDestinationTests(TestCase):
    def setUp(self):
        self.araku = make_destination(name='Araku Valley', slug='araku-valley', sort_order=10)
        self.vizag = make_destination(name='Vizag City', slug='vizag-city', sort_order=20)
        self.lamba = make_destination(name='Lambasingi', slug='lambasingi', sort_order=30)
        self.trip = make_page(slug='combo', title='Combo Trip', destination=self.araku)
        self.trip.also_visits.set([self.vizag, self.lamba])
        make_page(slug='solo', title='Solo Trip', destination=self.vizag)

    def titles(self, query):
        html = self.client.get('/tour-packages/' + query).content.decode()
        body = html[html.index('<main'):]
        return {t for t in ('Combo Trip', 'Solo Trip') if t in body}

    def test_places_lists_the_main_destination_first_without_duplicates(self):
        self.trip.also_visits.add(self.araku)
        self.assertEqual([d.slug for d in self.trip.places], ['araku-valley', 'vizag-city', 'lambasingi'])
        self.assertEqual(make_page(slug='nowhere', title='No Place').places, [])

    def test_place_filter_matches_every_place_a_trip_covers(self):
        self.assertEqual(self.titles('?destination=araku-valley'), {'Combo Trip'})
        self.assertEqual(self.titles('?destination=vizag-city'), {'Combo Trip', 'Solo Trip'})
        self.assertEqual(self.titles('?destination=lambasingi'), {'Combo Trip'})

    def test_a_place_only_reached_as_a_stop_still_gets_a_chip(self):
        html = self.client.get('/tour-packages/').content.decode()
        self.assertIn('destination=lambasingi', html)

    def test_the_trip_is_still_grouped_under_its_main_destination(self):
        html = self.client.get('/tour-packages/?destination=vizag-city').content.decode()
        body = html[html.index('<main'):]
        self.assertIn('Vizag City</h2>', body)
        self.assertEqual(body.count('Combo Trip</a>'), 1)  # once, not once per place

    def test_cards_say_which_places_a_multi_place_trip_covers(self):
        html = self.client.get('/tour-packages/').content.decode()
        self.assertIn('Covers Araku Valley · Vizag City · Lambasingi', html)
        self.assertEqual(html.count('class="trip-places"'), 1)  # single-place trips show nothing

    def test_draft_pages_and_their_stops_do_not_leak_chips(self):
        make_page(slug='hidden', title='Hidden', destination=self.araku, status='draft').also_visits.set(
            [make_destination(name='Secret Place', slug='secret-place')])
        self.assertNotIn('destination=secret-place', self.client.get('/tour-packages/').content.decode())

    def test_listing_uses_a_fixed_number_of_queries(self):
        for i in range(8):
            make_page(slug=f'extra-{i}', title=f'Extra {i}', destination=self.araku).also_visits.set([self.vizag])
        with self.assertNumQueries(self._query_count()):
            self.client.get('/tour-packages/')

    def _query_count(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        with CaptureQueriesContext(connection) as ctx:
            self.client.get('/tour-packages/')
        self.assertLess(len(ctx), 25)  # prefetched: does not grow with the number of trips
        return len(ctx)


class StopoverBackfillTests(TestCase):
    def test_fills_launch_packages_without_overwriting_admin_edits(self):
        from importlib import import_module

        from django.apps import apps
        migration = import_module('apps.core.migrations.0009_contentpage_also_visits')
        araku = make_destination(name='Araku Valley', slug='araku-valley')
        vizag = make_destination(name='Vizag', slug='vizag')
        lamba = make_destination(name='Lambasingi', slug='lambasingi')
        empty = make_page(slug='vizag-and-araku-3-days-tour-package', destination=araku)
        edited = make_page(slug='araku-lambasingi-tour-package', destination=lamba)
        edited.also_visits.set([vizag])
        migration.fill_launch_package_stops(apps, None)
        self.assertEqual([d.slug for d in empty.also_visits.all()], ['vizag'])
        self.assertEqual([d.slug for d in edited.also_visits.all()], ['vizag'])  # kept, not replaced

    def test_the_backfill_table_matches_the_seed(self):
        from importlib import import_module
        table = import_module('apps.core.migrations.0009_contentpage_also_visits').LAUNCH_PACKAGE_STOPS
        self.assertEqual(table, {i['slug']: i['also_visits'] for i in PACKAGES if i['also_visits']})
