from django import template
from django.templatetags.static import static
from django.utils.html import format_html

from apps.core import images

register = template.Library()

PHOTO_DIR = 'img/photos/'


def _src(photo, width):
    return static(f'{PHOTO_DIR}{photo.stem}-{width}.webp')


@register.simple_tag
def photo(key, css_class='', eager=False, sizes='100vw'):
    """An <img> for a registry photo: srcset, intrinsic size (no layout shift), registry alt text.

    eager=True is for the one large image at the top of a page (loads first); every other image is lazy.
    An unknown key renders nothing, so a typo can never break a page.
    """
    item = images.get(key)
    if item is None:
        return ''
    srcset = ', '.join(f'{_src(item, w)} {w}w' for w in sorted(item.widths))
    loading = format_html('loading="eager" fetchpriority="high"') if eager else format_html('loading="lazy"')
    return format_html(
        '<img src="{src}" srcset="{srcset}" sizes="{sizes}" width="{width}" height="{height}" alt="{alt}" '
        'class="{css_class}" {loading} decoding="async">',
        src=_src(item, min(item.widths)), srcset=srcset, sizes=sizes, width=item.width, height=item.height,
        alt=item.alt, css_class=css_class, loading=loading,
    )


@register.simple_tag(takes_context=True)
def photo_url(context, key, width=1600):
    """Absolute https URL of a photo (for Open Graph previews). Empty for an unknown key."""
    item = images.get(key)
    if item is None:
        return ''
    width = width if width in item.widths else item.largest
    return context['site']['base_url'] + _src(item, width)


@register.simple_tag
def photo_credit(key):
    """Short credit line for a figure caption; the full licence is on /photo-credits/."""
    item = images.get(key)
    return f'Photo: {item.author}, {item.licence}' if item else ''


@register.simple_tag
def photo_alt(key):
    item = images.get(key)
    return item.alt if item else ''
