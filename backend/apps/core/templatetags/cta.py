from urllib.parse import quote

from django import template
from django.conf import settings

register = template.Library()


def whatsapp_url(number, text):
    """wa.me link into the dedicated WhatsApp Business number. The prefill is fixed, non-sensitive text."""
    return f'https://wa.me/{number}?text={quote(text)}'


@register.inclusion_tag('partials/whatsapp_cta.html', takes_context=True)
def whatsapp_cta(context, text=None, label='Chat on WhatsApp', css_class='button button-whatsapp', icon=False,
                 where='', item=''):
    """A tracked WhatsApp link. Renders nothing when WHATSAPP_NUMBER is not configured.
    `where` (which button) and `item` (page slug) are analytics labels only, never visitor data."""
    site = context.get('site') or {}
    number = site.get('whatsapp_number', '')
    prefill = text or settings.WHATSAPP_PREFILL_TEXT
    return {
        'href': whatsapp_url(number, prefill) if number else '',
        'label': label,
        'css_class': css_class,
        'icon': icon,
        'send_to': (context.get('tracking') or {}).get('ads_whatsapp_send_to', ''),
        'where': where,
        'item': item,
    }


@register.inclusion_tag('partials/call_cta.html', takes_context=True)
def call_cta(context, label='Call us', css_class='button', icon=False, where='', item=''):
    """A tracked tel: link. Renders nothing when CONTACT_PHONE is not configured."""
    site = context.get('site') or {}
    return {
        'phone': site.get('contact_phone', ''),
        'label': label,
        'css_class': css_class,
        'icon': icon,
        'send_to': (context.get('tracking') or {}).get('ads_call_send_to', ''),
        'where': where,
        'item': item,
    }
