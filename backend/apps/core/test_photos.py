import re
from io import StringIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from . import images
from .models import ContentPage
from .test_content import PRICE_WORDS, FORBIDDEN_CLAIMS, make_page, text_of

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PHOTO_DIR = BACKEND_DIR / 'static' / 'img' / 'photos'
SITE = 'https://mytravelplanner.in'

try:
    from PIL import Image
except ImportError:  # Pillow is a dev-only dependency; the file-size checks need it
    Image = None


def img_tags(html):
    return re.findall(r'<img\b[^>]*>', html)


class RegistryTests(SimpleTestCase):
    def test_keys_and_stems_are_unique(self):
        keys = [p.key for p in images.PHOTOS]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len({p.stem for p in images.PHOTOS}), len(images.PHOTOS))

    def test_every_listed_file_exists_and_is_web_sized(self):
        for p in images.PHOTOS:
            self.assertIn(800, p.widths, p.key)
            for width in p.widths:
                path = PHOTO_DIR / f'{p.stem}-{width}.webp'
                self.assertTrue(path.is_file(), path)
                limit = 400 * 1024 if width == 1600 else 150 * 1024
                self.assertLess(path.stat().st_size, limit, f'{path.name} is too heavy for the web')

    def test_no_unlisted_files_in_the_photo_folder(self):
        listed = {f'{p.stem}-{w}.webp' for p in images.PHOTOS for w in p.widths}
        self.assertEqual({f.name for f in PHOTO_DIR.iterdir()}, listed)

    def test_registered_size_matches_the_real_largest_file(self):
        if Image is None:
            self.skipTest('Pillow not installed')
        for p in images.PHOTOS:
            with Image.open(PHOTO_DIR / f'{p.stem}-{p.largest}.webp') as im:
                self.assertEqual(im.size, (p.width, p.height), p.key)
                self.assertFalse(im.getexif(), f'{p.key} still carries EXIF metadata')

    def test_alt_text_is_present_and_reasonable(self):
        for p in images.PHOTOS:
            self.assertGreaterEqual(len(p.alt), 15, p.key)
            self.assertLessEqual(len(p.alt), 140, p.key)
            self.assertNotRegex(p.alt.lower(), r'\b(image|photo|picture) of\b', p.key)

    def test_every_photo_has_an_open_licence_author_and_source(self):
        for p in images.PHOTOS:
            self.assertIn(p.licence, images.ALLOWED_LICENCES, p.key)
            self.assertTrue(p.licence_url.startswith('https://creativecommons.org/'), p.key)
            self.assertTrue(p.source_url.startswith('https://commons.wikimedia.org/wiki/File:'), p.key)
            self.assertTrue(p.author.strip(), p.key)
            self.assertTrue(p.title.strip(), p.key)
            self.assertIn('Cropped', p.changes)

    def test_licence_whitelist_excludes_noncommercial_and_noderivatives(self):
        for name in images.ALLOWED_LICENCES:
            self.assertNotRegex(name, r'-(NC|ND)', name)

    def test_defaults_point_at_real_photos_and_gallery_is_big_enough(self):
        self.assertTrue(images.exists(images.DEFAULT_HERO))
        for page_type, key in images.DEFAULT_FOR_TYPE.items():
            self.assertTrue(images.exists(key), page_type)
        self.assertEqual(set(images.DEFAULT_FOR_TYPE), {'home', 'package', 'cab', 'guide'})
        self.assertGreaterEqual(len(images.gallery(limit=99)), 5)

    def test_explore_highlights_use_real_photos_and_make_no_claims(self):
        keys = [item.key for item in images.HIGHLIGHTS]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertGreaterEqual(len(keys), 4)
        self.assertNotIn(images.DEFAULT_HERO, keys)  # the hero photo is not repeated in the tiles
        for item in images.HIGHLIGHTS:
            self.assertTrue(images.exists(item.key), item.key)
            self.assertTrue(item.label.strip() and item.blurb.strip(), item.key)
            text = f'{item.label} {item.blurb}'.lower()
            self.assertIsNone(PRICE_WORDS.search(text), item.key)
            for phrase in FORBIDDEN_CLAIMS + ['best', 'must-visit', 'our ']:
                self.assertNotIn(phrase, text, f'{item.key}: {phrase}')

    def test_gallery_helper_excludes_and_limits(self):
        picked = images.gallery(exclude=['rainbow-hills'], limit=3)
        self.assertEqual(len(picked), 3)
        self.assertNotIn('rainbow-hills', [p.key for p in picked])

    def test_total_photo_weight_stays_modest(self):
        total = sum(f.stat().st_size for f in PHOTO_DIR.iterdir())
        self.assertLess(total, 3.5 * 1024 * 1024)  # whole library; a page loads only its own few photos


class PhotoTagTests(SimpleTestCase):
    def render(self, template, **ctx):
        return Template('{% load photos %}' + template).render(Context(ctx))

    def test_lazy_image_has_alt_size_srcset_and_small_fallback(self):
        html = self.render("{% photo 'rainbow-hills' css_class='card' sizes='50vw' %}")
        p = images.get('rainbow-hills')
        self.assertIn(f'alt="{p.alt}"', html)
        self.assertIn(f'width="{p.width}" height="{p.height}"', html)
        self.assertIn('loading="lazy"', html)
        self.assertNotIn('fetchpriority', html)
        self.assertIn('sizes="50vw"', html)
        self.assertIn('class="card"', html)
        self.assertRegex(html, r'src="[^"]*rainbow-hills-800\.webp"')
        self.assertRegex(html, r'srcset="[^"]*rainbow-hills-800\.webp 800w, [^"]*rainbow-hills-1600\.webp 1600w"')

    def test_eager_image_is_prioritised(self):
        html = self.render("{% photo 'valley-dusk' eager=True %}")
        self.assertIn('loading="eager" fetchpriority="high"', html)
        self.assertNotIn('loading="lazy"', html)

    def test_single_width_photo_only_lists_what_exists(self):
        html = self.render("{% photo 'borra-caves' %}")
        self.assertIn('borra-caves-800.webp 800w', html)
        self.assertNotIn('1600w', html)

    def test_unknown_key_renders_nothing(self):
        self.assertEqual(self.render("{% photo 'no-such-photo' %}"), '')
        self.assertEqual(self.render("{% photo_alt 'no-such-photo' as a %}[{{ a }}]"), '[]')

    def test_photo_url_is_absolute_and_falls_back_to_available_width(self):
        ctx = {'site': {'base_url': SITE}}
        url = self.render("{% photo_url 'valley-dusk' 1600 as u %}{{ u }}", **ctx)
        self.assertRegex(url, rf'^{re.escape(SITE)}/static/img/photos/valley-dusk-1600\.webp$')
        small = self.render("{% photo_url 'waterfall' 1600 as u %}{{ u }}", **ctx)
        self.assertTrue(small.endswith('waterfall-800.webp'))
        self.assertEqual(self.render("{% photo_url 'nope' as u %}[{{ u }}]", **ctx), '[]')


class HeroImageModelTests(TestCase):
    def test_unknown_hero_image_is_refused(self):
        with self.assertRaises(ValidationError) as ctx:
            ContentPage(page_type='guide', title='T', slug='t', hero_image='nope').full_clean()
        self.assertIn('hero_image', ctx.exception.message_dict)

    def test_known_or_blank_is_fine(self):
        for key in ('', 'borra-caves'):
            ContentPage(page_type='guide', title=f'T{key}', slug='t', hero_image=key).full_clean()

    def test_hero_key_defaults_by_page_type(self):
        for page_type, expected in images.DEFAULT_FOR_TYPE.items():
            page = ContentPage(page_type=page_type, title='x', slug='x')
            self.assertEqual(page.hero_key, expected, page_type)
        self.assertEqual(ContentPage(page_type='package', title='x', slug='x', hero_image='misty-pines').hero_key,
                         'misty-pines')


class AdminHeroImageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser('owner', 'o@example.test', 'a-long-test-password-1')

    def setUp(self):
        self.client.force_login(self.owner)

    def test_dropdown_lists_every_library_photo(self):
        html = self.client.get(reverse('admin:core_contentpage_add')).content.decode()
        self.assertIn('Default photo for this page type', html)
        for p in images.PHOTOS:
            self.assertIn(f'<option value="{p.key}">', html)

    def test_admin_saves_a_chosen_photo_and_rejects_a_fake_one(self):
        base = {'page_type': 'package', 'title': 'Admin Page', 'slug': 'admin-page', 'status': 'draft',
                'sort_order': '100'}
        ok = self.client.post(reverse('admin:core_contentpage_add'), {**base, 'hero_image': 'waterfall'})
        self.assertEqual(ok.status_code, 302)
        self.assertEqual(ContentPage.objects.get(slug='admin-page').hero_image, 'waterfall')
        bad = self.client.post(reverse('admin:core_contentpage_add'),
                               {**base, 'title': 'Other', 'slug': 'other', 'hero_image': 'not-a-photo'})
        self.assertEqual(bad.status_code, 200)
        self.assertFalse(ContentPage.objects.filter(slug='other').exists())


@override_settings(SITE_BASE_URL=SITE)
class PagesWithPhotosTests(TestCase):
    def test_homepage_hero_is_the_only_eager_image_and_everything_has_alt_and_size(self):
        make_page(slug='trip-one', title='Trip One')
        make_page(slug='trip-two', title='Trip Two', page_type='cab')
        html = self.client.get('/').content.decode()
        tags = img_tags(html)
        self.assertGreaterEqual(len(tags), 6)  # hero + 2 cards + gallery
        self.assertEqual(sum('fetchpriority="high"' in t for t in tags), 1)
        self.assertIn('hero-photo-img', next(t for t in tags if 'fetchpriority="high"' in t))
        for tag in tags:
            self.assertRegex(tag, r'alt="[^"]{10,}"', tag)
            self.assertRegex(tag, r'width="\d+" height="\d+"', tag)
            self.assertIn('srcset=', tag)
            self.assertIn('.webp', tag)

    def test_homepage_sections_how_it_works_cards_explore_tiles(self):
        make_page(slug='trip-one', title='Trip One', hero_image='misty-pines')
        html = self.client.get('/').content.decode()
        self.assertIn('How it works', html)
        self.assertEqual(html.count('class="how-step"'), 3)
        self.assertIn('Things to see around Araku, Lambasingi and Vizag', html)
        self.assertEqual(html.count('class="explore-tile"'), len(images.HIGHLIGHTS))
        for item in images.HIGHLIGHTS:
            self.assertIn(item.label, html)
            self.assertIn(f'{item.photo.stem}-800.webp', html)
        self.assertIn("not our partners' vehicles or services", html)
        self.assertIn(reverse('core:photo_credits'), html)
        self.assertIn('misty-pines-800.webp', html)  # the card uses the page's chosen photo

    def test_homepage_without_trips_still_has_hero_and_explore_tiles(self):
        html = self.client.get('/').content.decode()
        self.assertIn('hero-photo-img', html)
        self.assertIn('explore-grid', html)
        self.assertNotIn('trip-card-media', html)

    def test_content_page_banner_uses_its_photo_and_gallery_excludes_it(self):
        page = make_page(slug='banner', title='Banner', hero_image='rainbow-hills')
        html = self.client.get(reverse('core:content_page', args=[page.slug])).content.decode()
        banner = re.search(r'<div class="page-banner">(.*?)</div>', html, re.S).group(1)
        self.assertIn('rainbow-hills', banner)
        self.assertIn('fetchpriority="high"', banner)
        gallery = html[html.index('gallery-grid'):]
        self.assertNotIn('rainbow-hills', gallery)
        self.assertEqual(html.count('fetchpriority="high"'), 1)

    def test_content_page_without_choice_gets_the_default_for_its_type(self):
        page = make_page(slug='no-choice', title='No Choice', page_type='cab')
        html = self.client.get(reverse('core:content_page', args=[page.slug])).content.decode()
        self.assertIn('valley-road-800.webp', re.search(r'<div class="page-banner">(.*?)</div>', html, re.S).group(1))

    def test_pages_with_photos_still_state_no_prices_or_overclaims(self):
        make_page(slug='trip', title='Trip')
        for path in ('/', '/trip/', reverse('core:photo_credits')):
            text = text_of(self.client.get(path).content.decode()).lower()
            self.assertIsNone(PRICE_WORDS.search(text), path)
            for phrase in FORBIDDEN_CLAIMS:
                self.assertNotIn(phrase, text, f'{path}: {phrase}')

    def test_no_photo_shows_a_partner_claim(self):
        text = text_of(self.client.get('/').content.decode())
        self.assertNotIn('our fleet', text.lower())
        self.assertIn("not our partners' vehicles or services", text)  # the gallery says what the photos are


@override_settings(SITE_BASE_URL=SITE)
class OpenGraphAndIconTests(TestCase):
    def test_homepage_link_preview_tags(self):
        html = self.client.get('/').content.decode()
        self.assertIn('<meta property="og:site_name"', html)
        self.assertIn(f'<meta property="og:image" content="{SITE}/static/img/photos/valley-dusk-1600.webp">', html)
        self.assertIn(f'<meta property="og:image:alt" content="{images.get("valley-dusk").alt}">', html)
        self.assertIn('<meta property="og:type" content="website">', html)
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)
        self.assertIn(f'<meta property="og:url" content="{SITE}/">', html)

    def test_content_page_preview_uses_its_own_photo_title_and_description(self):
        page = make_page(slug='share', title='Share Me', meta_title='Share Title', meta_description='Share description.',
                         hero_image='galikonda-view')
        html = self.client.get(reverse('core:content_page', args=[page.slug])).content.decode()
        self.assertIn('<meta property="og:title" content="Share Title">', html)
        self.assertIn('<meta property="og:description" content="Share description.">', html)
        self.assertIn(f'<meta property="og:image" content="{SITE}/static/img/photos/galikonda-view-1600.webp">', html)
        self.assertIn(f'<meta property="og:url" content="{SITE}/share/">', html)

    def test_pages_without_a_photo_fall_back_to_the_default_preview_image(self):
        html = self.client.get(reverse('core:contact')).content.decode()
        self.assertIn('valley-dusk-1600.webp', html)

    def test_single_width_photo_preview_uses_the_available_file(self):
        page = make_page(slug='caves', title='Caves', hero_image='borra-caves')
        html = self.client.get(reverse('core:content_page', args=[page.slug])).content.decode()
        self.assertIn(f'content="{SITE}/static/img/photos/borra-caves-800.webp"', html)

    def test_favicon_is_linked_and_exists(self):
        self.assertIn('rel="icon" href="/static/img/favicon.svg"', self.client.get('/').content.decode())
        svg = (BACKEND_DIR / 'static' / 'img' / 'favicon.svg').read_text(encoding='utf-8')
        self.assertIn('<svg', svg)
        self.assertNotIn('<script', svg)


class PhotoCreditsTests(TestCase):
    def test_lists_every_photo_with_author_licence_and_source(self):
        response = self.client.get(reverse('core:photo_credits'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        for p in images.PHOTOS:
            self.assertIn(p.title, html, p.key)
            self.assertIn(p.author, html, p.key)
            self.assertIn(f'href="{p.licence_url}"', html, p.key)
            self.assertIn(f'href="{p.source_url}"', html, p.key)
            self.assertIn(p.licence, html, p.key)
        self.assertEqual(html.count('class="credit-item"'), len(images.PHOTOS))
        self.assertIn('cropped and resized', html.lower())
        self.assertIn("not photographs of any partner's vehicles", html)

    def test_credits_page_is_noindex_not_in_sitemap_and_linked_from_every_footer(self):
        self.assertContains(self.client.get(reverse('core:photo_credits')), 'content="noindex,follow"')
        self.assertNotIn('photo-credits', self.client.get('/sitemap.xml').content.decode())
        for name in ('core:contact', 'core:privacy', 'core:terms', 'core:enquiry', 'core:thank_you'):
            self.assertContains(self.client.get(reverse(name)), reverse('core:photo_credits'), msg_prefix=name)

    def test_slug_is_reserved_so_a_page_cannot_shadow_it(self):
        with self.assertRaises(ValidationError):
            ContentPage(page_type='guide', title='Credits', slug='photo-credits').full_clean()


class NoHotLinkingAndLayoutTests(SimpleTestCase):
    def test_templates_and_css_never_load_images_from_other_sites(self):
        for folder, pattern in (('templates', '*.html'), ('static/css', '*.css')):
            for path in (BACKEND_DIR / folder).rglob(pattern):
                text = path.read_text(encoding='utf-8')
                for host in ('upload.wikimedia.org', 'images.unsplash.com', 'pexels.com', 'pixabay.com'):
                    self.assertNotIn(host, text, f'{path.name} hot-links {host}')
                self.assertNotRegex(text, r'url\(\s*["\']?https?://', f'{path.name} loads a remote CSS image')
                self.assertNotRegex(text, r'<img[^>]+src="https?://', f'{path.name} has a remote <img>')

    def test_content_container_is_ninety_percent_of_the_screen(self):
        css = (BACKEND_DIR / 'static' / 'css' / 'site.css').read_text(encoding='utf-8')
        block = re.search(r'\.container\s*\{(.*?)\}', css, re.S).group(1)
        self.assertRegex(block, r'width:\s*90%')
        self.assertRegex(block, r'max-width:\s*var\(--max-width\)')
        self.assertRegex(css, r'--max-width:\s*1[5-9]\d\dpx')  # only capped on very large monitors

    def test_images_with_an_aspect_ratio_also_reset_the_height_attribute(self):
        # Every <img> carries its pixel height as an attribute (prevents layout shift). A rule that sets only
        # aspect-ratio would be stretched to that height (the tall-strip gallery bug), so it must say height: auto.
        css = (BACKEND_DIR / 'static' / 'css' / 'site.css').read_text(encoding='utf-8')
        for selector in ('gallery-img',):
            block = re.search(r'\.' + selector + r'\s*\{(.*?)\}', css, re.S).group(1)
            self.assertRegex(block, r'aspect-ratio', selector)
            self.assertRegex(block, r'height:\s*auto', selector)
        # Images that fill a fixed-ratio box instead must fill it completely.
        for selector in ('trip-card-img', 'page-banner-img', 'hero-photo-img', 'explore-img'):
            block = re.search(r'\.' + selector + r'\s*\{(.*?)\}', css, re.S).group(1)
            self.assertRegex(block, r'height:\s*100%', selector)
            self.assertRegex(block, r'object-fit:\s*cover', selector)

    def test_prose_keeps_a_readable_line_length(self):
        css = (BACKEND_DIR / 'static' / 'css' / 'site.css').read_text(encoding='utf-8')
        self.assertRegex(css, r'\.page-body-prose,\s*\.page-body-section\s*\{\s*max-width:\s*var\(--prose-width\)')

    def test_webp_is_served_with_the_right_content_type(self):
        import mimetypes
        from django.conf import settings
        self.assertEqual(mimetypes.guess_type('photo.webp')[0], 'image/webp')
        self.assertEqual(settings.WHITENOISE_MIMETYPES['.webp'], 'image/webp')

    def test_motion_can_be_turned_off(self):
        css = (BACKEND_DIR / 'static' / 'css' / 'site.css').read_text(encoding='utf-8')
        self.assertIn('prefers-reduced-motion: reduce', css)


class SeedHeroTests(TestCase):
    def test_seeded_araku_page_has_a_banner_photo(self):
        call_command('seed_launch_content', stdout=StringIO())
        page = ContentPage.objects.get(slug='araku-tour-packages')
        self.assertEqual(page.hero_image, 'galikonda-view')
        page.full_clean()
