"""Attribution captured on a campaign landing (apps.core.middleware) and copied onto a Lead at submit."""
from urllib.parse import urlparse

ATTRIBUTION_SESSION_KEY = 'attribution'
MAX_LENGTHS = {'landing_path': 200, 'utm_source': 100, 'utm_medium': 100, 'utm_campaign': 100, 'gclid': 255}


def _referer_path(request):
    """Path of the page the form was posted from, if it is on this site. Path only, never the query string."""
    referer = urlparse(request.META.get('HTTP_REFERER', ''))
    if referer.netloc and referer.netloc == request.get_host():
        return referer.path
    return ''


def get_attribution(request):
    """Attribution fields for a new Lead. Missing values are '' so attribution never blocks a lead."""
    stored = request.session.get(ATTRIBUTION_SESSION_KEY) or {}
    values = {field: str(stored.get(field, '')) for field in MAX_LENGTHS}
    if not values['landing_path']:
        values['landing_path'] = _referer_path(request)
    return {field: value[:MAX_LENGTHS[field]] for field, value in values.items()}
