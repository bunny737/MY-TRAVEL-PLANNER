from django.conf import settings
from django.core.cache import cache

DEFAULT_RATE = (5, 3600)


def parse_rate(rate):
    """'5/3600' -> (5, 3600): at most 5 requests per 3600 seconds. Falls back to the default on bad input."""
    try:
        count, seconds = rate.split('/')
        count, seconds = int(count), int(seconds)
    except (AttributeError, ValueError):
        return DEFAULT_RATE
    return (count, seconds) if count > 0 and seconds > 0 else DEFAULT_RATE


def client_ip(request):
    """The client IP from the configured proxy header, else REMOTE_ADDR.

    For a list header (X-Forwarded-For) only the entries our own proxies appended are trusted: the client IP is the
    CLIENT_IP_TRUSTED_HOPS-th from the right. Entries further left were written by the client and could be forged.
    """
    header = settings.CLIENT_IP_HEADER
    if header:
        value = request.META.get('HTTP_' + header.upper().replace('-', '_'), '')
        entries = [entry.strip() for entry in value.split(',') if entry.strip()]
        hops = max(settings.CLIENT_IP_TRUSTED_HOPS, 1)
        if len(entries) >= hops:
            return entries[-hops]
    return request.META.get('REMOTE_ADDR', '') or 'unknown'


def is_throttled(request, scope='leadform'):
    """Count this request against the client's budget; True once the budget for the window is spent."""
    limit, seconds = parse_rate(settings.LEAD_FORM_THROTTLE)
    key = f'throttle:{scope}:{client_ip(request)}'
    cache.add(key, 0, timeout=seconds)
    try:
        used = cache.incr(key)
    except ValueError:  # key expired between add() and incr()
        cache.set(key, 1, timeout=seconds)
        used = 1
    return used > limit
