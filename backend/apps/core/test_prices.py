"""Dated partner-quote prices (owner decision 2026-10-25, revised): every rupee amount on the site comes from the five
price fields, carries its quote date, hides itself when stale, and never names the partner."""
import re
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from . import content
from .models import ContentPage, Partner
from .test_content import PRICE_WORDS, make_page, text_of
from .test_leads import make_partner

PRICE_BLOCK = re.compile(r'<!--price-->.*?<!--/price-->', re.S)
PARTNER_NAME = 'Secret Hill Tours'


def quoted(days_ago=5):
    return timezone.localdate() - timedelta(days=days_ago)


def priced_page(days_ago=5, **overrides):
    partner = Partner.objects.filter(business_name=PARTNER_NAME).first() or make_partner(business_name=PARTNER_NAME)
    data = dict(
        price_from=Decimal('6000'), price_unit='per_couple', price_basis='AC sedan, 2 travellers, weekday',
        price_quoted_on=quoted(days_ago), price_partner=partner,
    )
    data.update(overrides)
    return make_page(**data)


def outside_price_blocks(html):
    return PRICE_BLOCK.sub(' ', html)


class FormatInrTests(SimpleTestCase):
    def test_whole_rupees_have_indian_grouping_and_no_decimals(self):
        self.assertEqual(content.format_inr(Decimal('6000')), '₹6,000')
        self.assertEqual(content.format_inr(Decimal('6000.00')), '₹6,000')
        self.assertEqual(content.format_inr(Decimal('22500')), '₹22,500')
        self.assertEqual(content.format_inr(Decimal('100000')), '₹1,00,000')
        self.assertEqual(content.format_inr(Decimal('1234567')), '₹12,34,567')
        self.assertEqual(content.format_inr(Decimal('999')), '₹999')

    def test_paise_are_kept_exactly(self):
        self.assertEqual(content.format_inr(Decimal('18500.50')), '₹18,500.50')


class ParsePriceOptionsTests(SimpleTestCase):
    def test_parses_label_bar_amount_as_decimal(self):
        rows = content.parse_price_options('2 days / 1 night | 15000\n3 days / 2 nights | 22,500\n\n')
        self.assertEqual(rows, [('2 days / 1 night', Decimal('15000')), ('3 days / 2 nights', Decimal('22500'))])
        self.assertIsInstance(rows[0][1], Decimal)

    def test_a_label_may_contain_a_bar_because_the_last_bar_splits(self):
        self.assertEqual(content.parse_price_options('A | B | 100'), [('A | B', Decimal('100'))])

    def test_bad_lines_are_refused(self):
        for bad in ('no amount here', '| 100', 'Label |', 'Label | abc', 'Label | 0', 'Label | -5', 'Label | NaN', 'Label | Infinity',
                    'x' * 81 + ' | 100'):
            with self.assertRaises(ValueError, msg=bad):
                content.parse_price_options(bad)

    def test_empty_text_has_no_options(self):
        self.assertEqual(content.parse_price_options(''), [])


class PriceOptionsTests(TestCase):
    OPTIONS = '2 days / 1 night | 15000\n3 days / 2 nights | 22500'

    def test_options_validate_with_the_price_and_are_stored_as_text(self):
        page = priced_page(slug='opts', title='Opts', price_options=self.OPTIONS)
        page.full_clean()

    def test_options_without_a_price_are_refused(self):
        page = ContentPage(page_type='package', title='T', slug='t', price_options=self.OPTIONS)
        with self.assertRaises(ValidationError) as ctx:
            page.full_clean()
        self.assertIn('price_from', ctx.exception.message_dict)

    def test_options_on_a_guide_are_refused(self):
        page = priced_page(slug='g', title='G', page_type='guide', price_options=self.OPTIONS)
        with self.assertRaises(ValidationError):
            page.full_clean()

    def test_a_bad_option_line_is_refused_on_save_in_admin(self):
        page = priced_page(slug='bad', title='Bad', price_options='2 days | lots')
        with self.assertRaises(ValidationError) as ctx:
            page.full_clean()
        self.assertIn('price_options', ctx.exception.message_dict)

    def test_options_show_with_the_date_inside_price_blocks_only(self):
        priced_page(slug='opts', title='Opts', price_options=self.OPTIONS, days_ago=3)
        html = self.client.get('/opts/').content.decode()
        blocks = ''.join(PRICE_BLOCK.findall(html))
        self.assertIn('2 days / 1 night', blocks)
        self.assertIn('₹22,500', blocks)
        self.assertIn(quoted(3).strftime('%-d %b %Y'), blocks)
        self.assertNotIn('₹', outside_price_blocks(html))
        self.assertNotIn(PARTNER_NAME, html)

    def test_options_hide_with_a_stale_quote(self):
        page = priced_page(slug='old', title='Old', price_options=self.OPTIONS, days_ago=200)
        self.assertIsNone(page.display_price)
        self.assertNotIn('₹', self.client.get('/old/').content.decode())

    def test_a_half_parsed_list_never_shows(self):
        page = priced_page(slug='half', title='Half', price_options='ok | 100\nbroken line')
        self.assertEqual(page.display_price['options'], [])

    def test_a_page_without_options_shows_no_options_section(self):
        priced_page(slug='plain', title='Plain')
        self.assertNotIn('price-options', self.client.get('/plain/').content.decode())


class PriceValidationTests(TestCase):
    def test_all_five_fields_or_none(self):
        page = ContentPage(page_type='package', title='T', slug='t', price_from=Decimal('6000'))
        with self.assertRaises(ValidationError) as ctx:
            page.full_clean()
        self.assertIn('price_from', ctx.exception.message_dict)
        ContentPage(page_type='package', title='T', slug='t').full_clean()

    def test_a_complete_price_is_valid_and_stored_as_decimal(self):
        page = priced_page(slug='ok', title='Ok')
        page.full_clean()
        page.refresh_from_db()
        self.assertIsInstance(page.price_from, Decimal)
        self.assertEqual(page.price_from, Decimal('6000.00'))

    def test_amount_must_be_above_zero(self):
        for amount in (Decimal('0'), Decimal('-5')):
            page = priced_page(slug=f'z{amount}', title=f'Z {amount}', price_from=amount)
            with self.assertRaises(ValidationError) as ctx:
                page.full_clean()
            self.assertIn('price_from', ctx.exception.message_dict)

    def test_quote_date_cannot_be_in_the_future(self):
        page = priced_page(slug='future', title='Future', days_ago=-3)
        with self.assertRaises(ValidationError) as ctx:
            page.full_clean()
        self.assertIn('price_quoted_on', ctx.exception.message_dict)

    def test_guides_articles_and_the_homepage_cannot_carry_a_price(self):
        for page_type in ('guide', 'article', 'home'):
            page = priced_page(slug=f'p-{page_type}', title=f'P {page_type}', page_type=page_type)
            with self.assertRaises(ValidationError) as ctx:
                page.full_clean()
            self.assertIn('price_from', ctx.exception.message_dict, page_type)

    def test_package_cab_and_stay_pages_can_carry_a_price(self):
        for page_type in ('package', 'cab', 'stay'):
            priced_page(slug=f'p-{page_type}', title=f'P {page_type}', page_type=page_type).full_clean()

    def test_the_partner_cannot_be_deleted_while_a_page_quotes_it(self):
        from django.db.models import ProtectedError
        page = priced_page()
        with self.assertRaises(ProtectedError):
            page.price_partner.delete()


class PriceDisplayTests(TestCase):
    def test_a_recent_price_shows_with_its_unit_basis_and_date(self):
        page = priced_page(slug='trip', title='Trip', days_ago=3)
        html = self.client.get('/trip/').content.decode()
        self.assertIn('₹6,000', html)
        self.assertIn('per couple', html)
        self.assertIn('AC sedan, 2 travellers, weekday', html)
        self.assertIn(quoted(3).strftime('%-d %b %Y'), html)
        self.assertIn('Quote dated ' + quoted(3).strftime('%-d %b %Y'), html)
        self.assertEqual(page.display_price['amount'], '₹6,000')

    def test_every_rupee_amount_sits_inside_a_dated_price_block(self):
        priced_page(slug='trip', title='Trip')
        html = self.client.get('/trip/').content.decode()
        self.assertGreaterEqual(len(PRICE_BLOCK.findall(html)), 2)  # fact strip and the quote box
        self.assertNotIn('₹', outside_price_blocks(html))
        for block in PRICE_BLOCK.findall(html):
            self.assertRegex(block, r'(?i:quote dated) \d{1,2} \w{3} \d{4}|\d{1,2} \w{3} \d{4}</span>')

    def test_the_rest_of_a_priced_page_has_no_price_words_or_overclaims(self):
        priced_page(slug='trip', title='Trip')
        text = text_of(outside_price_blocks(self.client.get('/trip/').content.decode()))
        self.assertIsNone(PRICE_WORDS.search(text), PRICE_WORDS.search(text))

    def test_the_partner_is_never_named_on_the_site(self):
        priced_page(slug='trip', title='Trip')
        for path in ('/trip/', '/', '/tour-packages/'):
            self.assertNotIn(PARTNER_NAME, self.client.get(path).content.decode(), path)

    def test_a_price_older_than_the_limit_hides_itself(self):
        page = priced_page(slug='old', title='Old', days_ago=91)
        self.assertIsNone(page.display_price)
        html = self.client.get('/old/').content.decode()
        self.assertNotIn('₹', html)
        self.assertEqual(PRICE_BLOCK.findall(html), [])

    @override_settings(PRICE_MAX_AGE_DAYS=10)
    def test_the_limit_comes_from_settings(self):
        self.assertIsNotNone(priced_page(slug='fresh', title='Fresh', days_ago=9).display_price)
        self.assertIsNone(priced_page(slug='stale', title='Stale', days_ago=11).display_price)

    def test_a_future_dated_row_never_shows(self):
        self.assertIsNone(priced_page(slug='future', title='Future', days_ago=-2).display_price)

    def test_a_page_without_a_price_shows_no_rupee_sign(self):
        make_page(slug='plain', title='Plain')
        self.assertNotIn('₹', self.client.get('/plain/').content.decode())

    def test_no_offer_product_or_rating_markup(self):
        priced_page(slug='trip', title='Trip')
        html = self.client.get('/trip/').content.decode()
        for banned in ('"Offer"', '"Product"', 'aggregateRating', 'priceCurrency', 'itemprop'):
            self.assertNotIn(banned, html)

    def test_cards_on_the_homepage_and_listing_show_the_dated_price(self):
        priced_page(slug='trip', title='Trip', days_ago=4)
        for path in ('/', '/tour-packages/'):
            html = self.client.get(path).content.decode()
            blocks = PRICE_BLOCK.findall(html)
            self.assertEqual(len(blocks), 1, path)
            self.assertIn('₹6,000', blocks[0])
            self.assertIn(quoted(4).strftime('%-d %b %Y'), blocks[0])
            self.assertNotIn('₹', outside_price_blocks(html), path)

    def test_a_stale_price_disappears_from_cards_too(self):
        priced_page(slug='old', title='Old', days_ago=200)
        for path in ('/', '/tour-packages/'):
            self.assertNotIn('₹', self.client.get(path).content.decode(), path)
