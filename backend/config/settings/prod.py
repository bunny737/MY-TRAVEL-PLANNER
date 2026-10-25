from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import ADMIN_URL_PATH, ALLOWED_HOSTS, CACHE_BACKEND, SECRET_KEY, SITE_BASE_URL, env

# Fail fast rather than start a misconfigured production site (docs/modules/01-foundation.md rule 1).
if env.bool('DEBUG', default=False):
    raise ImproperlyConfigured('DEBUG must not be enabled in production.')
DEBUG = False

if SECRET_KEY.startswith('dev-secret-key') or SECRET_KEY.startswith('change-me') or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured('SECRET_KEY must be a random value of at least 50 characters in production.')
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured('ALLOWED_HOSTS must be set in production.')
if not SITE_BASE_URL.startswith('https://'):
    raise ImproperlyConfigured('SITE_BASE_URL must be an https:// URL in production.')
if ADMIN_URL_PATH == 'admin/':
    raise ImproperlyConfigured('ADMIN_URL_PATH must not be the default "admin/" in production.')
if CACHE_BACKEND not in ('file', 'db'):
    raise ImproperlyConfigured('CACHE_BACKEND must be "file" (one host) or "db" (Cloud Run).')

# The admin holds lead phone numbers: a second factor is always required (Module 07, owner decision 2026-10-25).
if not env.bool('ADMIN_REQUIRE_MFA', default=True):
    raise ImproperlyConfigured('ADMIN_REQUIRE_MFA cannot be turned off in production.')
ADMIN_REQUIRE_MFA = True

# HTTPS everywhere. The reverse proxy must OVERWRITE X-Forwarded-Proto (never pass a client-sent value).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r'^health/$']  # liveness probe is called over plain HTTP by the proxy/host
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)  # raise after HTTPS is verified
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'

# Optional error reporting. Events must never carry lead PII, so default PII sending stays off.
_sentry_dsn = env('SENTRY_DSN', default='')
if _sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(dsn=_sentry_dsn, send_default_pii=False)
