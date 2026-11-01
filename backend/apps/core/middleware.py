import hmac
import re
from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponsePermanentRedirect

from .attribution import ATTRIBUTION_SESSION_KEY, MAX_LENGTHS


class EdgeSecretMiddleware:
    """403 for any request that did not come through our nginx edge, once EDGE_SHARED_SECRET is set.

    The service lives in its own GCP project, so Cloud Run's "internal" ingress cannot admit the edge VM; without this
    check anyone could call the *.run.app URL directly with a forged X-Forwarded-For and dodge the lead-form throttle.
    /health/ stays open for probes. A blank secret (development, tests, first smoke test) turns the check off.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        secret = settings.EDGE_SHARED_SECRET
        if secret and request.path != '/health/':
            sent = request.META.get('HTTP_X_TRAVEL_EDGE_KEY', '')
            if not hmac.compare_digest(sent.encode(), secret.encode()):
                return HttpResponseForbidden('Forbidden')
        return self.get_response(request)


class CanonicalHostMiddleware:
    """301 from an alias host (e.g. www.mytravelplanner.in) to the same path on the SITE_BASE_URL host.

    Only hosts listed in REDIRECT_TO_CANONICAL_HOSTS are redirected, so the Cloud Run *.run.app URL keeps working for
    smoke tests and nothing redirects in development. The query string is kept so ad click IDs (gclid/utm) survive.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        aliases = settings.REDIRECT_TO_CANONICAL_HOSTS
        if aliases and request.path != '/health/':
            # Raw header on purpose: Django still validates the host against ALLOWED_HOSTS later on.
            host = request.META.get('HTTP_HOST', '').split(':')[0].lower()
            if host in {alias.lower() for alias in aliases}:
                base = urlsplit(settings.SITE_BASE_URL)
                query = request.META.get('QUERY_STRING', '')
                return HttpResponsePermanentRedirect(
                    f'{base.scheme}://{base.netloc}{request.path}' + (f'?{query}' if query else ''))
        return self.get_response(request)

TRACKED_PARAMS = ('utm_source', 'utm_medium', 'utm_campaign', 'gclid')
_CONTROL_CHARS = re.compile(r'[\x00-\x1f\x7f]')


def _clean(value, limit):
    return _CONTROL_CHARS.sub('', value).strip()[:limit]


class AttributionMiddleware:
    """Remember which campaign click brought a visitor, so a later Lead can be attributed to it.

    Only a request that actually carries utm_*/gclid parameters writes anything, so organic visitors and crawlers never
    get a session row. The latest campaign click wins (a new ad click replaces the old attribution). Only the URL *path*
    is kept, never the query string, so nothing a visitor typed into a URL is stored.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._capture(request)
        return self.get_response(request)

    @staticmethod
    def _capture(request):
        if request.method not in ('GET', 'HEAD'):
            return
        path = request.path
        if path.startswith(('/static/', '/health/', '/' + settings.ADMIN_URL_PATH)):
            return
        found = {name: _clean(request.GET.get(name, ''), MAX_LENGTHS[name]) for name in TRACKED_PARAMS}
        found = {name: value for name, value in found.items() if value}
        if found:
            request.session[ATTRIBUTION_SESSION_KEY] = {'landing_path': path[:MAX_LENGTHS['landing_path']], **found}
