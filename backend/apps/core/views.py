from urllib.parse import quote, urlencode

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
    return ContentPage.objects.published().select_related('destination', 'price_partner').prefetch_related('also_visits')


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


TYPE_TABS = (
    ('all', 'All'),
    (ContentPage.PageType.PACKAGE.value, 'Tour packages'),
    (ContentPage.PageType.CAB.value, 'Cabs'),
    (ContentPage.PageType.STAY.value, 'Stays'),
)
# (query value, chip label, shortest day, longest day or None for "no upper limit")
DURATION_BUCKETS = (
    ('1', 'Day trip', 1, 1),
    ('2', '2 days / 1 night', 2, 2),
    ('3', '3 days / 2 nights', 3, 3),
    ('4', '4 days or more', 4, None),
)
SORT_OPTIONS = (
    ('recommended', 'Recommended'),
    ('shortest', 'Shortest trip first'),
    ('price', 'Lowest "from" price first'),
)
LISTING_DEFAULTS = {'type': 'all', 'destination': '', 'days': '', 'sort': 'recommended'}


def _listing_filters(params, page_types, destination_slugs):
    """The listing's filters from ?type=&destination=&days=&sort=. Anything unrecognised falls back to its default."""
    filters = dict(LISTING_DEFAULTS)
    if params.get('type') in page_types:
        filters['type'] = params['type']
    if params.get('destination') in destination_slugs:
        filters['destination'] = params['destination']
    if params.get('days') in {value for value, *_ in DURATION_BUCKETS}:
        filters['days'] = params['days']
    if params.get('sort') in dict(SORT_OPTIONS):
        filters['sort'] = params['sort']
    return filters


def _listing_href(filters, **changes):
    """/tour-packages/ plus only the non-default filters, so the unfiltered page keeps its plain address."""
    merged = {**filters, **changes}
    query = {key: value for key, value in merged.items() if value != LISTING_DEFAULTS[key]}
    base = reverse('core:tour_packages')
    return f'{base}?{urlencode(query)}' if query else base


def _in_day_range(page, shortest, longest):
    """A package matches when its day range overlaps the bucket's, so a "1 to 5 days" trip fits every length it covers."""
    if page.days_min is None or page.days_max is None:
        return False
    return page.days_min <= (longest if longest is not None else page.days_max) and page.days_max >= shortest


def _sorted_pages(pages, sort):
    """`recommended` keeps the admin order. `price` uses current dated prices only; the rest, and unpriced trips, go last."""
    pages = sorted(pages, key=lambda p: (p.sort_order, p.title))
    if sort == 'shortest':
        return sorted(pages, key=lambda p: (p.days_min is None, p.days_min or 0))
    if sort == 'price':
        return sorted(pages, key=lambda p: (not p.price_is_current, p.price_from if p.price_is_current else 0))
    return pages


@require_GET
def tour_packages(request):
    """Every published package, cab and stay page, with type, destination and trip-length filters and a sort.

    Filters are plain GET links (no JavaScript). The canonical stays /tour-packages/, so filtered URLs add no duplicates.
    """
    pages = list(_published_pages().filter(page_type__in=COMMERCIAL_TYPES))
    destinations = sorted({d for p in pages for d in p.places}, key=lambda d: (d.sort_order, d.name))
    # A tab for a type with no published pages would lead nowhere, so only types that exist are offered.
    tabs = [(value, label) for value, label in TYPE_TABS if value == 'all' or any(p.page_type == value for p in pages)]
    filters = _listing_filters(request.GET, {value for value, _ in tabs}, {d.slug for d in destinations})

    if filters['destination']:
        pages = [p for p in pages if any(d.slug == filters['destination'] for d in p.places)]
    show_type = filters['type']
    bucket = next((b for b in DURATION_BUCKETS if b[0] == filters['days']), None)
    if bucket:
        # Only packages carry a length in days, so choosing one leaves cabs and stays out.
        show_type = ContentPage.PageType.PACKAGE.value

    def of_type(page_type):
        if show_type not in ('all', page_type):
            return []
        chosen = [p for p in pages if p.page_type == page_type]
        if bucket and page_type == ContentPage.PageType.PACKAGE:
            chosen = [p for p in chosen if _in_day_range(p, bucket[2], bucket[3])]
        return _sorted_pages(chosen, filters['sort'])

    packages = of_type(ContentPage.PageType.PACKAGE)
    cabs = of_type(ContentPage.PageType.CAB)
    stays = of_type(ContentPage.PageType.STAY)
    recommended = filters['sort'] == 'recommended'
    is_filtered = any(filters[key] != LISTING_DEFAULTS[key] for key in ('type', 'destination', 'days'))
    return render(request, 'pages/tour_packages.html', {
        # Recommended order groups packages by destination; any other sort shows one flat, visibly ordered list.
        'package_groups': _group_by_destination(packages) if recommended else [],
        'packages': [] if recommended else packages,
        'cabs': cabs,
        'stays': stays,
        'has_results': bool(packages or cabs or stays),
        'result_count': len(packages) + len(cabs) + len(stays),
        'filters': filters,
        'is_filtered': is_filtered,
        'type_tabs': [
            {'label': label, 'href': _listing_href(filters, type=value, days=''), 'active': show_type == value}
            for value, label in tabs
        ] if len(tabs) > 2 else [],
        'destination_chips': [
            {'label': 'All places', 'href': _listing_href(filters, destination=''), 'active': not filters['destination']},
            *[{'label': d.name, 'href': _listing_href(filters, destination=d.slug), 'active': filters['destination'] == d.slug}
              for d in destinations],
        ] if len(destinations) > 1 else [],
        'duration_chips': [
            {'label': 'Any length', 'href': _listing_href(filters, days=''), 'active': not bucket},
            *[{'label': label, 'href': _listing_href(filters, days=value), 'active': filters['days'] == value}
              for value, label, *_ in DURATION_BUCKETS],
        ],
        'show_duration_chips': filters['type'] in ('all', ContentPage.PageType.PACKAGE.value),
        'sort_options': [{'value': value, 'label': label, 'selected': filters['sort'] == value} for value, label in SORT_OPTIONS],
        'clear_href': reverse('core:tour_packages'),
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
