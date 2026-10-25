import json
import re
import xml.etree.ElementTree as ET
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from . import content
from .models import ContentPage, Destination

PRICE_WORDS = re.compile(r'(₹|\bRs\.?\s*\d|\bINR\b|\bprice|\bcost\s+of\b|/-)', re.I)
FORBIDDEN_CLAIMS = ['cheapest', 'guaranteed', 'instant confirmation', 'verified', 'best price', '5-star', 'official']


def make_page(**overrides):
    n = ContentPage.objects.count() + 1
    data = dict(
        page_type='package', title=f'Test Package {n}', slug=f'test-package-{n}',
        intro='Independent partners send you quotes.', meta_description=f'Description number {n}.',
        status='published',
    )
    data.update(overrides)
    return ContentPage.objects.create(**data)


def text_of(html):
    html = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()


class ParsingTests(SimpleTestCase):
    def test_list_ignores_blank_lines_and_whitespace_and_crlf(self):
        self.assertEqual(content.parse_list('  Cab \r\n\r\n Driver  \n\n'), ['Cab', 'Driver'])
        self.assertEqual(content.parse_list(''), [])

    def test_paragraphs_join_wrapped_lines(self):
        self.assertEqual(content.parse_paragraphs('one\ntwo\n\n\nthree'), ['one two', 'three'])

    def test_blocks_first_line_is_heading(self):
        blocks = content.parse_blocks('Day 1\nDrive up\nStop\r\n\r\nDay 2\nReturn')
        self.assertEqual([b.heading for b in blocks], ['Day 1', 'Day 2'])
        self.assertEqual(blocks[0].lines, ('Drive up', 'Stop'))
        self.assertEqual(blocks[1].lines, ('Return',))

    def test_heading_only_block(self):
        self.assertEqual(content.parse_blocks('Just a heading')[0].lines, ())


class ContentPageModelTests(TestCase):
    def test_homepage_slug_is_forced_and_only_one_allowed(self):
        home = make_page(page_type='home', slug='whatever', title='Home')
        self.assertEqual(home.slug, 'home')
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_page(page_type='home', title='Second home')

    def test_published_at_is_stamped_once(self):
        page = make_page(status='draft')
        self.assertIsNone(page.published_at)
        page.status = 'published'
        page.save()
        first = page.published_at
        self.assertIsNotNone(first)
        page.title = 'Renamed'
        page.save()
        self.assertEqual(page.published_at, first)

    def test_reserved_slugs_are_refused(self):
        for slug in ('contact', 'privacy', 'terms', 'enquiry', 'thank-you', 'health', 'admin', 'sitemap', 'home'):
            with self.assertRaises(ValidationError, msg=slug) as ctx:
                ContentPage(page_type='guide', title=f't-{slug}', slug=slug).full_clean()
            self.assertIn('slug', ctx.exception.message_dict, slug)

    @override_settings(ADMIN_URL_PATH='manage-x/')
    def test_configured_admin_path_is_reserved(self):
        with self.assertRaises(ValidationError) as ctx:
            ContentPage(page_type='guide', title='x', slug='manage-x').full_clean()
        self.assertIn('slug', ctx.exception.message_dict)

    def test_canonical_override_must_be_https_or_a_path(self):
        for bad in ('http://example.test/x', 'example.test/x', 'ftp://x'):
            with self.assertRaises(ValidationError, msg=bad) as ctx:
                ContentPage(page_type='guide', title='T', slug='t', canonical_override=bad).full_clean()
            self.assertIn('canonical_override', ctx.exception.message_dict)
        for good in ('', '/other-page/', 'https://example.test/x'):
            ContentPage(page_type='guide', title='T', slug='t', canonical_override=good).full_clean()

    def test_canonical_url(self):
        page = make_page(slug='araku-x')
        self.assertEqual(page.canonical_url('https://site.test/'), 'https://site.test/araku-x/')
        page.canonical_override = '/elsewhere/'
        self.assertEqual(page.canonical_url('https://site.test'), 'https://site.test/elsewhere/')
        page.canonical_override = 'https://other.test/p/'
        self.assertEqual(page.canonical_url('https://site.test'), 'https://other.test/p/')

    def test_duplicate_search_titles_refused_case_insensitively(self):
        make_page(title='Araku Tours', meta_title='Araku Tours Quote')
        with self.assertRaises(ValidationError) as ctx:
            ContentPage(page_type='guide', title='Other', slug='other', meta_title='araku tours QUOTE').full_clean()
        self.assertIn('meta_title', ctx.exception.message_dict)

    def test_blank_meta_title_falls_back_to_title_for_the_uniqueness_check(self):
        make_page(title='Same Heading')
        with self.assertRaises(ValidationError) as ctx:
            ContentPage(page_type='guide', title='same heading', slug='other').full_clean()
        self.assertIn('meta_title', ctx.exception.message_dict)

    def test_duplicate_descriptions_refused(self):
        make_page(meta_description='Exactly the same words.')
        with self.assertRaises(ValidationError) as ctx:
            ContentPage(page_type='guide', title='Another', slug='another',
                        meta_description='exactly the same words.').full_clean()
        self.assertIn('meta_description', ctx.exception.message_dict)

    def test_a_page_does_not_clash_with_itself(self):
        page = make_page()
        page.full_clean()

    def test_publishing_needs_description_and_intro(self):
        page = ContentPage(page_type='guide', title='G', slug='g', status='published')
        with self.assertRaises(ValidationError) as ctx:
            page.full_clean()
        self.assertIn('meta_description', ctx.exception.message_dict)
        self.assertIn('intro', ctx.exception.message_dict)
        ContentPage(page_type='guide', title='G', slug='g', status='draft').full_clean()

    def test_there_are_no_price_fields(self):
        names = {f.name for f in ContentPage._meta.get_fields()}
        self.assertFalse([n for n in names if re.search(r'price|cost|fee|amount|rate', n)], names)

    def test_helpers_for_forms_and_links(self):
        self.assertEqual(make_page(page_type='package', slug='a').form_service, 'tour')
        self.assertEqual(make_page(page_type='cab', slug='b').form_service, 'cab')
        guide = make_page(page_type='guide', slug='c')
        self.assertFalse(guide.has_form)
        self.assertEqual(guide.cta_href, reverse('core:enquiry'))
        self.assertEqual(make_page(page_type='package', slug='d').cta_href, '#quote')
        self.assertEqual(make_page(page_type='home', slug='x', title='H').whatsapp_prefill, '')


@override_settings(SITE_BASE_URL='https://site.test', WHATSAPP_NUMBER='919000000000')
class ContentPageViewTests(TestCase):
    def setUp(self):
        self.page = make_page(
            title='Araku Tour Packages', slug='araku-tour-packages', meta_title='Araku Tours: Free Quotes',
            meta_description='Quotes for Araku trips.', duration='Day trip, or 2 days / 1 night',
            body='First paragraph.\n\nSecond paragraph.',
            itinerary='Day trip (example)\nDrive up the ghat\nBorra Caves',
            faq='Is it free?\nYes, asking is free.',
        )

    def get(self, page=None):
        return self.client.get(reverse('core:content_page', args=[(page or self.page).slug]))

    def test_published_page_renders_with_seo_basics(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertEqual(html.count('<h1>'), 1)
        self.assertIn('<title>Araku Tours: Free Quotes</title>', html)
        self.assertIn('name="description" content="Quotes for Araku trips."', html)
        self.assertIn('<link rel="canonical" href="https://site.test/araku-tour-packages/">', html)
        self.assertIn('content="index,follow"', html)
        self.assertIn('Last updated', html)
        self.assertIn('Day trip, or 2 days / 1 night', html)

    def test_title_falls_back_to_page_title_plus_site_name(self):
        page = make_page(meta_title='', title='Plain Title', slug='plain-title')
        with override_settings(SITE_NAME='Test Brand'):
            self.assertIn('<title>Plain Title | Test Brand</title>', self.get(page).content.decode())

    def test_canonical_override_is_used(self):
        page = make_page(slug='dup', canonical_override='/araku-tour-packages/')
        self.assertIn('href="https://site.test/araku-tour-packages/"', self.get(page).content.decode())

    def test_drafts_and_the_homepage_row_are_not_served_at_a_slug(self):
        draft = make_page(status='draft', slug='secret-draft')
        self.assertEqual(self.get(draft).status_code, 404)
        make_page(page_type='home', slug='home', title='Home')
        self.assertEqual(self.client.get('/home/').status_code, 404)
        self.assertEqual(self.client.get('/no-such-page/').status_code, 404)

    def test_unpublishing_takes_the_page_offline(self):
        self.page.status = 'draft'
        self.page.save()
        self.assertEqual(self.get().status_code, 404)

    def test_sections_render_from_admin_text(self):
        html = self.get().content.decode()
        for expected in ('Example itinerary', 'Day trip (example)', 'Drive up the ghat', 'Borra Caves',
                         'Frequently asked questions', 'Is it free?', 'Yes, asking is free.',
                         'First paragraph.', 'Second paragraph.'):
            self.assertIn(expected, html)

    def test_empty_sections_are_not_rendered(self):
        html = self.get().content.decode()
        self.assertNotIn('What a quote usually includes', html)
        self.assertNotIn('What is usually not included', html)
        bare = make_page(slug='bare', itinerary='', faq='', body='')
        html = self.get(bare).content.decode()
        for heading in ('Example itinerary', 'Frequently asked questions'):
            self.assertNotIn(heading, html)

    def test_inclusions_and_exclusions_render_as_lists_when_given(self):
        self.page.inclusions = 'Cab with driver\nParking and toll'
        self.page.exclusions = 'Entry tickets'
        self.page.save()
        html = self.get().content.decode()
        self.assertIn('What a quote usually includes', html)
        self.assertIn('<li>Cab with driver</li>', html)
        self.assertIn('<li>Parking and toll</li>', html)
        self.assertIn('What is usually not included', html)
        self.assertIn('<li>Entry tickets</li>', html)

    def test_editor_text_is_escaped(self):
        page = make_page(slug='xss', intro='<script>alert(1)</script>', body='<b>bold</b> & more',
                         itinerary='<img src=x onerror=alert(1)>\n<i>line</i>', title='T <u>x</u>')
        html = self.get(page).content.decode()
        for raw in ('<script>alert(1)</script>', '<b>bold</b>', '<img src=x', '<i>line</i>', '<u>x</u>'):
            self.assertNotIn(raw, html, raw)
        self.assertIn('&lt;b&gt;bold&lt;/b&gt; &amp; more', html)

    def test_package_page_has_one_form_preselected_and_two_cta_rows(self):
        html = self.get().content.decode()
        self.assertEqual(html.count('<form'), 1)
        self.assertEqual(html.count('id="quote"'), 1)
        self.assertIn('<option value="tour" selected>', html)
        self.assertEqual(html.count('class="cta-row"'), 2)  # near the top and again after the content
        self.assertIn('We are a travel enquiry and referral platform', html)
        self.assertIn('Hi%2C%20I%20want%20a%20quote%20for%20Araku%20Tour%20Packages.', html)
        self.assertIn('data-track="whatsapp_click"', html)

    def test_cab_page_preselects_cab(self):
        cab = make_page(page_type='cab', slug='vizag-to-araku-cab', title='Vizag to Araku Cab')
        self.assertIn('<option value="cab" selected>', self.get(cab).content.decode())

    def test_guide_page_has_links_not_a_form(self):
        guide = make_page(page_type='guide', slug='araku-guide', title='Araku Guide')
        html = self.get(guide).content.decode()
        self.assertEqual(html.count('<form'), 0)
        self.assertIn(f'href="{reverse("core:enquiry")}"', html)
        self.assertIn('We are a travel enquiry and referral platform', html)

    def test_breadcrumb_structured_data_is_valid_json(self):
        html = self.get().content.decode()
        raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
        data = json.loads(raw)
        self.assertEqual(data['@type'], 'BreadcrumbList')
        self.assertEqual([i['position'] for i in data['itemListElement']], [1, 2])
        self.assertEqual(data['itemListElement'][1]['item'], 'https://site.test/araku-tour-packages/')

    def test_structured_data_cannot_break_out_of_its_script_tag(self):
        page = make_page(slug='tricky', title='Evil </script><script>alert(1)</script>')
        html = self.get(page).content.decode()
        block = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
        self.assertNotIn('<', block)
        self.assertEqual(json.loads(block)['itemListElement'][1]['name'], page.title)

    def test_no_review_or_product_markup(self):
        html = self.get().content.decode()
        for banned in ('AggregateRating', '"Review"', '"Product"', 'ratingValue', '"Offer"'):
            self.assertNotIn(banned, html)

    def test_pages_state_no_prices_and_no_overclaims(self):
        text = text_of(self.get().content.decode())
        self.assertIsNone(PRICE_WORDS.search(text), PRICE_WORDS.search(text))
        for phrase in FORBIDDEN_CLAIMS:
            self.assertNotIn(phrase, text.lower(), phrase)


@override_settings(SITE_BASE_URL='https://site.test')
class HomePageTests(TestCase):
    def test_default_homepage_without_any_content(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('<h1>Plan your Araku, Lambasingi or Vizag trip</h1>', html)
        self.assertIn('Compare suitable tour and cab options from independent local travel providers. Request quotes free.', html)
        self.assertIn('We are a travel enquiry and referral platform', html)
        self.assertEqual(html.count('<form'), 1)
        self.assertIn('<link rel="canonical" href="https://site.test/">', html)
        self.assertIn('content="index,follow"', html)
        self.assertNotIn('Trips you can ask about', html)

    def test_published_home_page_overrides_the_defaults(self):
        make_page(page_type='home', slug='home', title='Your Araku Holiday', meta_title='Araku Holidays',
                  intro='Custom intro text.', meta_description='Custom home description.', body='Home body.')
        html = self.client.get('/').content.decode()
        self.assertIn('<h1>Your Araku Holiday</h1>', html)
        self.assertIn('Custom intro text.', html)
        self.assertIn('<title>Araku Holidays</title>', html)
        self.assertIn('Custom home description.', html)
        self.assertIn('Home body.', html)
        self.assertNotIn('Plan your Araku, Lambasingi or Vizag trip', html)

    def test_draft_home_page_is_ignored(self):
        make_page(page_type='home', slug='home', title='Draft Home', status='draft')
        self.assertIn('<h1>Plan your Araku, Lambasingi or Vizag trip</h1>', self.client.get('/').content.decode())

    def test_lists_only_published_package_and_cab_pages_in_order(self):
        make_page(title='Second Trip', slug='second', sort_order=20, duration='2 days')
        make_page(title='First Trip', slug='first', sort_order=10, page_type='cab')
        make_page(title='Hidden Draft', slug='hidden', status='draft')
        make_page(title='A Guide', slug='a-guide', page_type='guide')
        html = self.client.get('/').content.decode()
        self.assertIn('Trips you can ask about', html)
        self.assertLess(html.index('First Trip'), html.index('Second Trip'))
        self.assertIn('href="/first/"', html)
        for absent in ('Hidden Draft', 'A Guide'):
            self.assertNotIn(absent, html)

    def test_no_prices_on_the_homepage(self):
        make_page(title='Trip', slug='trip')
        text = text_of(self.client.get('/').content.decode())
        self.assertIsNone(PRICE_WORDS.search(text))


@override_settings(SITE_BASE_URL='https://site.test', ADMIN_URL_PATH='admin/')
class SitemapAndRobotsTests(TestCase):
    def locs(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        root = ET.fromstring(response.content)
        return root, [u.find('s:loc', ns).text for u in root.findall('s:url', ns)]

    def test_lists_home_published_pages_and_trust_pages_only(self):
        make_page(slug='live', title='Live')
        make_page(slug='guide-live', title='Guide Live', page_type='guide')
        make_page(slug='draft-one', title='Draft', status='draft')
        make_page(page_type='home', slug='home', title='Home')
        _, locs = self.locs()
        self.assertEqual(sorted(locs), sorted([
            'https://site.test/', 'https://site.test/live/', 'https://site.test/guide-live/',
            'https://site.test/destinations/', 'https://site.test/contact/', 'https://site.test/privacy/', 'https://site.test/terms/',
        ]))

    def test_never_lists_form_thank_you_or_admin_urls(self):
        make_page(slug='live', title='Live')
        _, locs = self.locs()
        for loc in locs:
            for path in ('/enquiry/', '/thank-you/', '/admin', '/health'):
                self.assertNotIn(path, loc)

    def test_homepage_is_listed_even_without_a_home_row(self):
        self.assertIn('https://site.test/', self.locs()[1])

    def test_lastmod_for_pages_and_canonical_override(self):
        make_page(slug='moved', title='Moved', canonical_override='/new-home/')
        root, locs = self.locs()
        self.assertIn('https://site.test/new-home/', locs)
        lastmods = [e.text for e in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')]
        self.assertEqual(len(lastmods), 1)  # only the content page has a real modification date
        self.assertRegex(lastmods[0], r'^\d{4}-\d{2}-\d{2}$')

    def test_robots_txt(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response['Content-Type'], 'text/plain')
        body = response.content.decode()
        self.assertIn('User-agent: *', body)
        self.assertIn('Disallow: /admin/', body)
        self.assertIn('Disallow: /thank-you/', body)
        self.assertIn('Sitemap: https://site.test/sitemap.xml', body)
        # /enquiry/ is linked and noindex: it must stay crawlable or the noindex is never seen.
        self.assertNotIn('/enquiry/', body)

    @override_settings(ADMIN_URL_PATH='manage-x/')
    def test_robots_follows_the_configured_admin_path(self):
        self.assertIn('Disallow: /manage-x/', self.client.get('/robots.txt').content.decode())


class ContentAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser('owner', 'o@example.test', 'a-long-test-password-1')

    def setUp(self):
        self.client.force_login(self.owner)

    def test_requires_login(self):
        self.client.logout()
        for name in ('admin:core_contentpage_changelist', 'admin:core_destination_changelist'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 302, name)

    def test_changelist_filters_and_live_link(self):
        make_page(title='Live One', slug='live-one')
        make_page(title='Draft One', slug='draft-one', status='draft')
        response = self.client.get(reverse('admin:core_contentpage_changelist'), {'status__exact': 'published'})
        self.assertContains(response, 'Live One')
        self.assertNotContains(response, 'Draft One')
        self.assertContains(response, 'href="/live-one/"')

    def test_publish_action_publishes_valid_drafts_and_refuses_incomplete_ones(self):
        good = make_page(slug='good', title='Good', status='draft')
        bad = make_page(slug='bad', title='Bad', status='draft', meta_description='')
        response = self.client.post(reverse('admin:core_contentpage_changelist'), {
            'action': 'publish_pages', '_selected_action': [good.pk, bad.pk],
        }, follow=True)
        good.refresh_from_db()
        bad.refresh_from_db()
        self.assertEqual(good.status, 'published')
        self.assertIsNotNone(good.published_at)
        self.assertEqual(bad.status, 'draft')
        self.assertContains(response, 'not published')
        self.assertEqual(self.client.get('/good/').status_code, 200)
        self.assertEqual(self.client.get('/bad/').status_code, 404)

    def test_unpublish_action(self):
        page = make_page(slug='gone', title='Gone')
        self.client.post(reverse('admin:core_contentpage_changelist'), {
            'action': 'unpublish_pages', '_selected_action': [page.pk],
        })
        self.assertEqual(self.client.get('/gone/').status_code, 404)

    def test_add_page_in_admin_rejects_reserved_slug_and_duplicate_description(self):
        make_page(slug='first', title='First', meta_description='Same text.')
        response = self.client.post(reverse('admin:core_contentpage_add'), {
            'page_type': 'guide', 'title': 'Contact', 'slug': 'contact', 'status': 'draft', 'sort_order': '100',
            'meta_description': 'same text.',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContentPage.objects.count(), 1)
        self.assertContains(response, 'used by another part of the site')
        self.assertContains(response, 'already has this search description')

    def test_destination_admin_creates_a_destination(self):
        response = self.client.post(reverse('admin:core_destination_add'), {
            'name': 'Lambasingi', 'slug': 'lambasingi', 'summary': '', 'is_active': 'on', 'sort_order': '100',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Destination.objects.filter(slug='lambasingi').exists())


class SeedCommandTests(TestCase):
    def run_seed(self):
        out = StringIO()
        call_command('seed_launch_content', stdout=out)
        return out.getvalue()

    def test_creates_a_draft_that_is_not_public(self):
        self.run_seed()
        page = ContentPage.objects.get(slug='araku-tour-packages')
        self.assertEqual(page.status, 'draft')
        self.assertIsNone(page.published_at)
        self.assertEqual(page.destination.slug, 'araku-valley')
        self.assertEqual(self.client.get('/araku-tour-packages/').status_code, 404)

    def test_is_idempotent_and_never_overwrites_edits(self):
        self.run_seed()
        page = ContentPage.objects.get(slug='araku-tour-packages')
        page.intro = 'My edited intro.'
        page.save()
        self.assertIn('already exists', self.run_seed())
        self.assertEqual(ContentPage.objects.count(), 4)  # Araku, Lambasingi, Vizag and the Vizag to Araku cab drafts
        page.refresh_from_db()
        self.assertEqual(page.intro, 'My edited intro.')

    def test_seed_content_is_valid_to_publish_and_contains_no_prices_or_overclaims(self):
        self.run_seed()
        page = ContentPage.objects.get(slug='araku-tour-packages')
        page.status = 'published'
        page.full_clean()  # meta lengths, uniqueness, intro: all satisfied
        page.save()
        html = self.client.get('/araku-tour-packages/').content.decode()
        text = text_of(html)
        self.assertIsNone(PRICE_WORDS.search(text), PRICE_WORDS.search(text))
        for phrase in FORBIDDEN_CLAIMS:
            self.assertNotIn(phrase, text.lower(), phrase)
        self.assertNotIn('What a quote usually includes', html)  # operator-confirmed inclusions are left for the owner
        self.assertIn('Example itinerary', html)
        self.assertIn('Are you the tour operator?', html)
        self.assertIn('Day trip, or 2 days / 1 night', html)

    def test_seed_notes_tell_the_owner_to_verify(self):
        self.run_seed()
        self.assertIn('Before publishing', ContentPage.objects.get(slug='araku-tour-packages').internal_notes)
