from urllib.parse import quote

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from . import images
from .attribution import get_attribution
from .forms import EnquiryForm
from .models import ContentPage, Destination, Lead
from .notifications import notify_new_lead
from .seo import breadcrumb_jsonld
from .throttle import is_throttled

# Session flags carry booleans only, never personal data. Module 06 reads/clears CONVERSION_PENDING.
CONVERSION_PENDING = 'lead_conversion_pending'


@require_GET
@never_cache
def health(request):
    """Liveness probe: no DB access and no detail, so it can never leak data."""
    return HttpResponse('ok', content_type='text/plain')


COMMERCIAL_TYPES = (ContentPage.PageType.PACKAGE, ContentPage.PageType.CAB, ContentPage.PageType.STAY)
HOME_TRIP_LIMIT = 6
RELATED_LIMIT = 6


def _published_pages():
    return ContentPage.objects.published().select_related('destination', 'price_partner')


def _related_pages(page):
    """Other published pages for the same destination, commercial pages first. Drafts and the page itself never appear."""
    if not page.destination_id:
        return []
    others = _published_pages().filter(destination_id=page.destination_id).exclude(pk=page.pk).exclude(
        page_type=ContentPage.PageType.HOME,
    )
    ranked = sorted(others, key=lambda other: (other.page_type not in COMMERCIAL_TYPES, other.sort_order, other.title))
    return ranked[:RELATED_LIMIT]


def _group_by_destination(pages):
    """[{'destination': Destination or None, 'pages': [...]}] in destination order, pages without a destination last."""
    groups = {}
    for page in pages:
        groups.setdefault(page.destination, []).append(page)
    ordered = sorted(groups, key=lambda d: (d is None, d.sort_order if d else 0, d.name if d else ''))
    return [{'destination': d, 'pages': groups[d]} for d in ordered]


@require_GET
def home(request):
    """The homepage. Uses the published `home` page if there is one, otherwise a built-in default so the site never 404s."""
    page = _published_pages().filter(page_type=ContentPage.PageType.HOME).first()
    trips = _published_pages().filter(page_type__in=COMMERCIAL_TYPES)
    hero_key = page.hero_key if page else images.DEFAULT_HERO
    return render(request, 'pages/home.html', {
        'page': page,
        'trips': list(trips[:HOME_TRIP_LIMIT]),
        'more_trips': trips.count() > HOME_TRIP_LIMIT,
        'hero_key': hero_key,
        'og_image_key': hero_key,
        'highlights': images.HIGHLIGHTS,
        'canonical_url': page.canonical_url(settings.SITE_BASE_URL) if page else settings.SITE_BASE_URL.rstrip('/') + '/',
    })


@require_GET
def content_page(request, slug):
    """Any published package, cab or guide page, at /<slug>/. Drafts and the homepage row are not served here."""
    page = get_object_or_404(_published_pages().exclude(page_type=ContentPage.PageType.HOME), slug=slug)
    is_article = page.page_type == ContentPage.PageType.ARTICLE
    canonical_url = page.canonical_url(settings.SITE_BASE_URL)
    return render(request, 'pages/content_page.html', {
        'page': page,
        'hero_key': page.hero_key,
        'og_image_key': page.hero_key,
        'gallery': images.gallery(exclude=[page.hero_key], limit=3,
                                  place=page.destination.slug if page.destination else None),
        'related_pages': _related_pages(page),
        'canonical_url': canonical_url,
        # Only the page's own title and address: no tracking, no visitor data.
        'share_url': 'https://wa.me/?text=' + quote(f'{page.title} {canonical_url}') if is_article else '',
        'breadcrumb_json': breadcrumb_jsonld(
            page, settings.SITE_BASE_URL, settings.SITE_NAME, parent=('Blog', reverse('core:blog')) if is_article else None,
        ),
    })


@require_GET
def tour_packages(request):
    """Every published package, cab and stay page, grouped by destination."""
    pages = list(_published_pages().filter(page_type__in=COMMERCIAL_TYPES))
    by_type = lambda page_type: [p for p in pages if p.page_type == page_type]  # noqa: E731
    return render(request, 'pages/tour_packages.html', {
        'package_groups': _group_by_destination(by_type(ContentPage.PageType.PACKAGE)),
        'cabs': by_type(ContentPage.PageType.CAB),
        'stays': by_type(ContentPage.PageType.STAY),
        'og_image_key': 'rainbow-hills',
    })


@require_GET
def blog(request):
    """Published articles, newest first. ?destination=<slug> filters them; the canonical stays /blog/ so filters add no duplicates."""
    posts = _published_pages().filter(page_type=ContentPage.PageType.ARTICLE).order_by('-published_at', 'sort_order')
    chips = Destination.objects.filter(is_active=True, pages__in=posts).distinct()
    selected = chips.filter(slug=request.GET.get('destination', '')).first()
    if selected:
        posts = posts.filter(destination=selected)
    return render(request, 'pages/blog.html', {
        'posts': posts, 'chips': chips, 'selected': selected, 'og_image_key': 'galikonda-view',
    })


@require_GET
def sitemap(request):
    """Indexable pages only: the homepage, published content pages and the trust pages. No form, thank-you or admin URLs."""
    base = settings.SITE_BASE_URL.rstrip('/')
    pages = _published_pages()
    home_page = pages.filter(page_type=ContentPage.PageType.HOME).first()
    entries = [{'loc': base + '/', 'lastmod': home_page.updated_at if home_page else None}]
    entries += [
        {'loc': page.canonical_url(base), 'lastmod': page.updated_at}
        for page in pages.exclude(page_type=ContentPage.PageType.HOME)
    ]
    entries += [
        {'loc': base + reverse(name), 'lastmod': None}
        for name in ('core:tour_packages', 'core:blog', 'core:destinations', 'core:contact', 'core:privacy', 'core:terms')
    ]
    return render(request, 'sitemap.xml', {'entries': entries}, content_type='application/xml')


@require_GET
def destinations(request):
    """Every active destination with its live pages. Cards and links come from the destinations template tag."""
    return render(request, 'pages/destinations.html', {'og_image_key': 'galikonda-view'})


@require_GET
def photo_credits(request):
    """Attribution for every photo on the site (required by the CC BY / CC BY-SA licences)."""
    return render(request, 'pages/photo_credits.html', {'photos': images.PHOTOS})


@require_GET
def robots(request):
    """Blocks only what should never be crawled. /enquiry/ is linked and `noindex`, so it must stay crawlable for that tag to be seen."""
    lines = [
        'User-agent: *',
        f'Disallow: /{settings.ADMIN_URL_PATH}',
        'Disallow: /thank-you/',
        '',
        f'Sitemap: {settings.SITE_BASE_URL.rstrip("/")}/sitemap.xml',
        '',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


@require_http_methods(['GET', 'POST'])
def enquiry(request):
    """The short enquiry form. GET shows it; POST saves a Lead. Never returns lead data."""
    if request.method == 'GET':
        return render(request, 'pages/enquiry.html', {'form': EnquiryForm()})

    if is_throttled(request):
        return render(request, 'pages/enquiry.html', {'form': EnquiryForm(), 'throttled': True}, status=429)

    # Honeypot: pretend it worked so a bot learns nothing, but save nothing and fire no conversion.
    if request.POST.get('website'):
        return redirect('core:thank_you')

    form = EnquiryForm(request.POST)
    if not form.is_valid():
        return render(request, 'pages/enquiry.html', {'form': form})

    lead = form.save(commit=False)
    lead.lead_channel = Lead.Channel.FORM
    lead.is_duplicate = Lead.is_duplicate_submission(lead.phone, lead.service_type)
    for field, value in get_attribution(request).items():
        setattr(lead, field, value)
    lead.save()

    if not lead.is_duplicate:
        # A duplicate is kept for the founder but is not counted again by analytics or notifications.
        request.session[CONVERSION_PENDING] = True
        notify_new_lead(lead)
    return redirect('core:thank_you')


@require_GET
@never_cache
def thank_you(request):
    # Popped, so a refresh or a revisit never reports the same lead twice.
    fire_conversion = request.session.pop(CONVERSION_PENDING, False)
    return render(request, 'pages/thank_you.html', {'fire_conversion': fire_conversion})
