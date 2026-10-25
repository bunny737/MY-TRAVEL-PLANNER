"""Blog and guide bodies: headings, contents box, in-text photos, destination filter, WhatsApp share link."""
import json
import re
from urllib.parse import parse_qs, urlparse

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase, override_settings

from . import content, images
from .models import ContentPage
from .test_content import FORBIDDEN_CLAIMS, PRICE_WORDS, make_page, text_of
from .test_destinations import make_destination

BODY = (
    'Intro paragraph.\n\n## First stop\nSome words here.\nMore words.\n\n[photo: borra-caves]\n\n'
    '## Second stop\nText.\n\n## Second stop\nSame heading again.\n\n## Last\nEnd.'
)


def article(**overrides):
    n = ContentPage.objects.count() + 1
    data = dict(page_type='article', title=f'Article {n}', slug=f'article-{n}', body=BODY)
    data.update(overrides)
    return make_page(**data)


class ParseArticleTests(SimpleTestCase):
    def test_headings_photos_and_paragraphs(self):
        kinds = [(s.kind, s.text) for s in content.parse_article(BODY)]
        self.assertEqual(kinds[0], ('paragraph', 'Intro paragraph.'))
        self.assertEqual(kinds[1], ('heading', 'First stop'))
        self.assertEqual(kinds[2], ('paragraph', 'Some words here. More words.'))
        self.assertEqual(kinds[3], ('photo', 'borra-caves'))

    def test_heading_anchors_are_unique(self):
        anchors = [s.anchor for s in content.parse_article(BODY) if s.kind == 'heading']
        self.assertEqual(anchors, ['first-stop', 'second-stop', 'second-stop-2', 'last'])

    def test_a_heading_line_ends_the_paragraph_before_it(self):
        segments = content.parse_article('Before\n## Heading\nAfter')
        self.assertEqual([(s.kind, s.text) for s in segments],
                         [('paragraph', 'Before'), ('heading', 'Heading'), ('paragraph', 'After')])

    def test_plain_text_without_markers_is_just_paragraphs(self):
        self.assertEqual([s.kind for s in content.parse_article('One\n\nTwo')], ['paragraph', 'paragraph'])

    def test_a_hash_without_text_is_not_a_heading(self):
        self.assertEqual(content.parse_article('## ')[0].kind, 'paragraph')


class ArticleValidationTests(TestCase):
    def test_unknown_photo_key_is_refused_on_articles_and_guides(self):
        for page_type in ('article', 'guide'):
            page = ContentPage(page_type=page_type, title='T', slug=f't-{page_type}', body='[photo: not-a-photo]')
            with self.assertRaises(ValidationError) as ctx:
                page.full_clean()
            self.assertIn('body', ctx.exception.message_dict)

    def test_known_photo_key_is_accepted(self):
        ContentPage(page_type='article', title='T', slug='t', body='[photo: borra-caves]').full_clean()

    def test_blog_and_tour_packages_slugs_are_reserved(self):
        for slug in ('blog', 'tour-packages'):
            with self.assertRaises(ValidationError):
                ContentPage(page_type='guide', title='X', slug=slug).full_clean()


@override_settings(SITE_BASE_URL='https://site.test')
class ArticlePageTests(TestCase):
    def test_headings_get_ids_and_a_contents_box_appears_from_three(self):
        article(slug='long')
        html = self.client.get('/long/').content.decode()
        self.assertIn('<h2 id="first-stop">First stop</h2>', html)
        self.assertIn('<h2 id="second-stop-2">Second stop</h2>', html)
        self.assertIn('aria-label="Contents"', html)
        self.assertIn('href="#last"', html)

    def test_no_contents_box_for_fewer_than_three_headings(self):
        article(slug='short', body='Text\n\n## One\nA\n\n## Two\nB')
        self.assertNotIn('aria-label="Contents"', self.client.get('/short/').content.decode())

    def test_heading_text_is_escaped(self):
        article(slug='xss', body='## <script>alert(1)</script>\nText')
        html = self.client.get('/xss/').content.decode()
        self.assertNotIn('<script>alert(1)', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)

    def test_in_text_photo_is_a_lazy_registry_image_with_credit(self):
        article(slug='pics')
        html = self.client.get('/pics/').content.decode()
        photo = images.get('borra-caves')
        self.assertIn(f'alt="{photo.alt}"', html)
        self.assertIn(f'Photo: {photo.author}, {photo.licence}', html)
        self.assertEqual(html.count('fetchpriority="high"'), 1)  # only the hero is eager

    def test_guides_use_the_same_body_format(self):
        make_page(page_type='guide', slug='guide', title='Guide', body='## Part one\nText')
        self.assertIn('<h2 id="part-one">Part one</h2>', self.client.get('/guide/').content.decode())

    def test_articles_have_no_form_and_link_to_the_enquiry_page(self):
        article(slug='a')
        html = self.client.get('/a/').content.decode()
        self.assertNotIn('name="consent_given"', html)
        self.assertIn('href="/enquiry/"', html)
        self.assertIn('referral-disclosure', html)

    def test_article_shows_publish_date_and_read_time_but_no_price_or_free_quote_fact(self):
        article(slug='a')
        text = text_of(self.client.get('/a/').content.decode())
        self.assertRegex(text, r'\d+ min Read')
        self.assertIn('Published', text)
        self.assertNotIn('To request a quote', text)
        self.assertNotIn('₹', text)

    def test_breadcrumb_markup_and_json_include_the_blog(self):
        article(slug='a', title='My Article')
        html = self.client.get('/a/').content.decode()
        self.assertIn('<a href="/blog/">Blog</a>', html)
        data = json.loads(re.search(r'application/ld\+json">(.*?)</script>', html, re.S).group(1))
        names = [item['name'] for item in data['itemListElement']]
        self.assertEqual(names[1:], ['Blog', 'My Article'])
        self.assertEqual(data['itemListElement'][1]['item'], 'https://site.test/blog/')

    def test_share_link_carries_only_the_title_and_address(self):
        article(slug='a', title='My Article')
        html = self.client.get('/a/').content.decode()
        href = re.search(r'href="(https://wa\.me/\?text=[^"]+)"', html).group(1).replace('&amp;', '&')
        text = parse_qs(urlparse(href).query)['text'][0]
        self.assertEqual(text, 'My Article https://site.test/a/')

    def test_share_link_is_not_a_tracked_whatsapp_click(self):
        article(slug='a')
        html = self.client.get('/a/').content.decode()
        tag = re.search(r'<a [^>]*href="https://wa\.me/\?text=[^>]*>', html).group(0)
        self.assertNotIn('data-track', tag)

    def test_only_articles_get_a_share_link(self):
        make_page(slug='pkg', title='Pkg')
        self.assertNotIn('https://wa.me/?text=', self.client.get('/pkg/').content.decode())

    def test_article_text_has_no_prices_or_overclaims(self):
        article(slug='a')
        text = text_of(self.client.get('/a/').content.decode()).lower()
        self.assertIsNone(PRICE_WORDS.search(text))
        for word in FORBIDDEN_CLAIMS:
            self.assertNotIn(word, text)


@override_settings(SITE_BASE_URL='https://site.test')
class BlogIndexTests(TestCase):
    def test_lists_published_articles_newest_first_and_nothing_else(self):
        old = article(slug='old', title='Older Post')
        new = article(slug='new', title='Newer Post')
        ContentPage.objects.filter(pk=old.pk).update(published_at='2026-01-01T00:00:00Z')
        ContentPage.objects.filter(pk=new.pk).update(published_at='2026-06-01T00:00:00Z')
        article(slug='draft', title='Draft Post', status='draft')
        make_page(slug='a-guide', title='A Guide Page', page_type='guide')
        make_page(slug='a-package', title='A Package Page')
        html = self.client.get('/blog/').content.decode()
        self.assertLess(html.index('Newer Post'), html.index('Older Post'))
        for absent in ('Draft Post', 'A Guide Page', 'A Package Page'):
            self.assertNotIn(absent, html.split('class="post-list"')[1])

    def test_empty_blog_still_renders(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('No articles here yet', response.content.decode())

    def test_filter_by_destination(self):
        araku = make_destination(name='Araku Valley', slug='araku-valley')
        vizag = make_destination(name='Vizag', slug='vizag')
        article(slug='a1', title='Araku Post', destination=araku)
        article(slug='v1', title='Vizag Post', destination=vizag)
        html = self.client.get('/blog/?destination=vizag').content.decode()
        listing = html.split('class="post-list"')[1]
        self.assertIn('Vizag Post', listing)
        self.assertNotIn('Araku Post', listing)
        self.assertIn('href="/blog/?destination=araku-valley"', html)

    def test_unknown_destination_falls_back_to_all_posts(self):
        article(slug='a1', title='Araku Post')
        response = self.client.get('/blog/?destination=nowhere')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Araku Post', response.content.decode())

    def test_filter_chips_only_for_destinations_with_posts_and_only_when_useful(self):
        araku = make_destination(name='Araku Valley', slug='araku-valley')
        make_destination(name='Empty Place', slug='empty-place')
        article(slug='a1', title='Araku Post', destination=araku)
        html = self.client.get('/blog/').content.decode()
        self.assertNotIn('Filter by destination', html)  # one destination: nothing to choose
        vizag = make_destination(name='Vizag', slug='vizag')
        article(slug='v1', title='Vizag Post', destination=vizag)
        html = self.client.get('/blog/').content.decode()
        self.assertIn('Filter by destination', html)
        chips = html[html.index('class="chip-row"'):html.index('</nav>', html.index('class="chip-row"'))]
        self.assertNotIn('Empty Place', chips)  # no posts, so no chip (it is still in the site-wide Destinations menu)
        self.assertIn('Araku Valley', chips)

    def test_canonical_is_always_the_blog_index_and_filters_are_not_in_the_sitemap(self):
        make_destination(name='Vizag', slug='vizag')
        html = self.client.get('/blog/?destination=vizag').content.decode()
        self.assertIn('<link rel="canonical" href="https://site.test/blog/">', html)
        sitemap = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('https://site.test/blog/', sitemap)
        self.assertNotIn('destination=', sitemap)

    def test_articles_are_in_the_sitemap_drafts_are_not(self):
        article(slug='live', title='Live Post')
        article(slug='draft', title='Draft Post', status='draft')
        sitemap = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('https://site.test/live/', sitemap)
        self.assertNotIn('/draft/', sitemap)

    def test_has_unique_title_description_and_one_h1(self):
        html = self.client.get('/blog/').content.decode()
        self.assertEqual(html.count('<h1'), 1)
        self.assertRegex(html, r'<title>[^<]*Blog[^<]*</title>')
        self.assertRegex(html, r'<meta name="description" content="[^"]{40,}')
