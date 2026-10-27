"""Page layout v2: full-width colour bands, one <h1> per page, honest homepage sections, accessible colours."""
import re
from pathlib import Path

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .test_content import FORBIDDEN_CLAIMS, PRICE_WORDS, make_page, text_of

CSS = (Path(__file__).resolve().parent.parent.parent / 'static' / 'css' / 'site.css').read_text(encoding='utf-8')
INNER_PAGES = ('core:contact', 'core:privacy', 'core:terms', 'core:enquiry', 'core:photo_credits')


def css_block(selector):
    return re.search(re.escape(selector) + r'\s*\{(.*?)\}', CSS, re.S).group(1)


class PageStructureTests(TestCase):
    def test_main_is_full_width_and_content_sits_in_a_container(self):
        for name in INNER_PAGES:
            html = self.client.get(reverse(name)).content.decode()
            self.assertIn('<main id="main" class="site-main">', html, name)
            self.assertIn('class="container page-body"', html, name)
            self.assertEqual(html.count('<h1>'), 1, name)
            self.assertIn('class="band band-mint page-hero"', html, name)

    def test_legal_pages_show_their_update_date_in_the_header(self):
        for name in ('core:privacy', 'core:terms'):
            html = self.client.get(reverse(name)).content.decode()
            header = html[html.index('page-hero'):html.index('</header>', html.index('page-hero'))]
            self.assertIn('Last updated: 25 October 2026', header, name)
            self.assertIn('class="legal-card"', html, name)

    def test_homepage_bands_in_order(self):
        make_page(slug='trip', title='Trip')
        html = self.client.get('/').content.decode()
        order = ['home-hero', 'promise-strip', 'destinations-section', 'trips-section', 'explore-section', 'how-section', 'quote-band']
        positions = [html.index(marker) for marker in order]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn('class="container page-body"', html)  # the homepage lays out its own bands

    def test_disclosure_sits_near_the_top_of_the_homepage(self):
        html = self.client.get('/').content.decode()
        disclosure = html.index('We are a travel enquiry and referral platform')
        self.assertLess(disclosure, html.index('explore-section'))

    @override_settings(WHATSAPP_NUMBER='', CONTACT_PHONE='')
    def test_closing_chat_band_only_when_a_number_is_configured(self):
        self.assertNotIn('closing-cta', self.client.get('/').content.decode())
        with override_settings(WHATSAPP_NUMBER='919000000000'):
            self.assertIn('closing-cta', self.client.get('/').content.decode())

    def test_homepage_has_no_reviews_ratings_prices_or_overclaims(self):
        # The reference design has a testimonials band; we have no genuine reviews, so there is none (invariant 3).
        make_page(slug='trip', title='Trip')
        text = text_of(self.client.get('/').content.decode()).lower()
        for word in ('review', 'testimonial', 'rated', 'stars', '★', 'happy customers', 'travellers say'):
            self.assertNotIn(word, text, word)
        for phrase in FORBIDDEN_CLAIMS:
            self.assertNotIn(phrase, text, phrase)
        self.assertIsNone(PRICE_WORDS.search(text))

    def test_package_page_has_photo_hero_fact_strip_form_aside_and_closing_band(self):
        page = make_page(slug='pkg', title='Pkg', duration='1 day')
        html = self.client.get(reverse('core:content_page', args=[page.slug])).content.decode()
        self.assertIn('class="page-photo-hero"', html)
        strip = html[html.index('fact-strip'):html.index('</ul>', html.index('fact-strip'))]
        for fact in ('1 day', 'Trip length', 'Tour package', 'Last updated'):
            self.assertIn(fact, strip)
        self.assertIn('detail-layout has-aside', html)
        self.assertIn('id="quote" class="quote-box quote-box-aside"', html)
        self.assertIn('band band-forest cta-band', html)

    def test_guide_page_has_no_form_aside_and_no_quote_fact(self):
        page = make_page(slug='guide', title='Guide', page_type='guide')
        html = self.client.get(reverse('core:content_page', args=[page.slug])).content.decode()
        self.assertNotIn('has-aside', html)
        self.assertIn('Travel guide', html)
        self.assertNotIn('To request a quote', html)

    @override_settings(WHATSAPP_NUMBER='919000000000', CONTACT_PHONE='+919000000001', CONTACT_EMAIL='hi@example.com')
    def test_footer_contact_column_and_floating_buttons_not_in_header(self):
        html = self.client.get(reverse('core:privacy')).content.decode()
        footer = html[html.index('<footer'):]
        self.assertIn('Get in touch', footer)
        self.assertIn('mailto:hi@example.com', footer)
        self.assertIn('href="tel:+919000000001"', footer)
        self.assertIn('data-track="call_click"', footer)
        self.assertIn('data-track="whatsapp_click"', footer)
        header = html[html.index('<header class="site-header">'):html.index('</header>')]
        self.assertNotIn('wa.me', header)
        self.assertNotIn('tel:', header)
        float_cta = html[html.index('class="float-cta"'):]
        self.assertIn('wa.me/919000000000', float_cta)
        self.assertIn('href="tel:+919000000001"', float_cta)
        self.assertIn('href="mailto:hi@example.com"', float_cta)

    def test_404_uses_the_page_header(self):
        response = self.client.get('/no-such-page/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'page-hero', status_code=404)
        self.assertContains(response, '<h1>Page not found</h1>', status_code=404)


def _luminance(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def token(name):
    return re.search(r'--' + name + r':\s*#([0-9a-fA-F]{6})', CSS).group(1)


class ColourContrastTests(SimpleTestCase):
    """WCAG AA (4.5:1) for text colour pairs the design actually uses."""

    def test_text_pairs_meet_aa(self):
        white = 'ffffff'
        pairs = [
            (white, token('primary')),                       # buttons, green band
            (white, token('primary-hover')),
            (white, token('whatsapp')),                      # WhatsApp button
            (token('text-main'), token('accent-gold')),      # saffron button
            (token('text-main'), token('accent-gold-hover')),
            (token('text-sec'), token('bg-page')),
            (token('text-muted'), token('bg-page')),
            (token('text-muted'), token('bg-mint')),
            (token('text-sec'), token('bg-sand')),
            (token('accent-terracotta-text'), token('bg-page')),   # eyebrows
            (token('accent-terracotta-text'), token('bg-mint')),
            (token('accent-terracotta-text'), token('bg-sand')),
            (token('accent-gold-text'), token('bg-page')),
            (token('primary'), token('bg-mint')),             # links on mint
            ('d6d3cd', token('bg-charcoal')),                 # footer text
            ('f6d9a8', token('primary')),                     # light eyebrow on the green band
        ]
        for fg, bg in pairs:
            self.assertGreaterEqual(contrast(fg, bg), 4.5, f'#{fg} on #{bg}')

    def test_saffron_buttons_never_use_white_text(self):
        block = css_block('.button.button-saffron,\na.button.button-saffron')
        self.assertIn('color: var(--text-main)', block)
        self.assertLess(contrast('ffffff', token('accent-gold')), 4.5)  # why: white on saffron is unreadable

    def test_outline_link_buttons_are_not_white_on_white(self):
        self.assertIn('color: var(--primary)', css_block('a.button.button-outline'))
