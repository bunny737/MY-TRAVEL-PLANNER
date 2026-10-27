from django import template
from django.urls import reverse

from apps.core.models import ContentPage, Destination

register = template.Library()


def destination_entries():
    """Active destinations, each with where a visitor should go: its live page, else its card on /destinations/.

    Draft pages are never linked. Built from the database, so publishing a page in admin updates every menu.
    """
    destinations = list(Destination.objects.filter(is_active=True))
    live = {}
    for page in ContentPage.objects.published().filter(destination__in=destinations).exclude(page_type='home'):
        live.setdefault(page.destination_id, []).append(page)
    hub = reverse('core:destinations')
    entries = []
    for destination in destinations:
        pages = live.get(destination.pk, [])
        primary = next(
            (page for page_type in ('package', 'cab', 'guide') for page in pages if page.page_type == page_type), None,
        )
        entries.append({
            'destination': destination,
            'pages': pages,
            'primary': primary,
            'href': primary.get_absolute_url() if primary else f'{hub}#{destination.slug}',
        })
    return entries


@register.inclusion_tag('partials/destination_menu.html', takes_context=True)
def destination_menu(context, variant='nav'):
    """The Destinations menu (variant='nav') or the footer list (variant='footer')."""
    request = context.get('request')
    return {
        'entries': destination_entries(),
        'variant': variant,
        'current_path': request.path if request else '',
        'hub_url': reverse('core:destinations'),
    }


NAV_MENU_LIMIT = 8


@register.inclusion_tag('partials/page_menu.html', takes_context=True)
def page_menu(context, label, page_types, all_url):
    """A nav dropdown of published pages of the given types (comma-separated), e.g. {% page_menu "Tour packages" "package" url %}.

    With nothing published the menu is not drawn, so a visitor is never offered an empty list. Drafts are never linked.
    """
    request = context.get('request')
    types = page_types.split(',')
    pages = list(ContentPage.objects.published().filter(page_type__in=types)[:NAV_MENU_LIMIT])
    return {
        'label': label, 'pages': pages, 'all_url': all_url,
        'current_path': request.path if request else '',
    }


@register.inclusion_tag('partials/destination_cards.html', takes_context=True)
def destination_cards(context, heading_level=3):
    return {'entries': destination_entries(), 'heading_level': heading_level, 'site': context.get('site')}
