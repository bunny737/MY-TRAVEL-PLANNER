import mimetypes
import tempfile
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR.parent / '.env')

SECRET_KEY = env('SECRET_KEY', default='dev-secret-key-change-in-prod')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# Admin lives at a configurable path (obscure it in production). Normalised to "path/" with no leading slash.
ADMIN_URL_PATH = env('ADMIN_URL_PATH', default='admin/').strip('/') + '/'

INSTALLED_APPS = [
    'config.apps.MfaAdminConfig',  # django.contrib.admin with a second factor (config/admin_site.py)
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_otp',
    'django_otp.plugins.otp_totp',
    # local apps
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.core.middleware.CanonicalHostMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'apps.core.middleware.AttributionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='travel_platform'),
        'USER': env('DB_USER', default='app_user'),
        'PASSWORD': env('DB_PASSWORD', default='app_password'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {'sslmode': env('DB_SSLMODE', default='prefer')},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# English only at launch (docs/open-decisions.md). Times are shown in IST.
LANGUAGE_CODE = 'en-in'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# The slim Docker image has no system MIME table, so tell Python (dev server) and WhiteNoise (production) about WebP.
mimetypes.add_type('image/webp', '.webp')
WHITENOISE_MIMETYPES = {'.webp': 'image/webp'}

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Email (optional; admin check is enough at tiny volume) ---
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='') or 'noreply@localhost'

# --- Site config (CLAUDE.md invariant 9): reaches templates only via apps.core.context_processors ---
SITE_NAME = env('SITE_NAME', default='Travel Planner (placeholder)')
SITE_BASE_URL = env('SITE_BASE_URL', default='http://localhost:8100')
WHATSAPP_NUMBER = env('WHATSAPP_NUMBER', default='')
# Pre-filled first message in the WhatsApp chat. Must stay generic: never put a name, phone or trip details here.
WHATSAPP_PREFILL_TEXT = env('WHATSAPP_PREFILL_TEXT', default='Hi, I want a tour quote.')
CONTACT_EMAIL = env('CONTACT_EMAIL', default='')
CONTACT_PHONE = env('CONTACT_PHONE', default='')
RESPONSE_HOURS_TEXT = env('RESPONSE_HOURS_TEXT', default='')
CONSENT_NOTICE_VERSION = env('CONSENT_NOTICE_VERSION', default='2026-10-v1')
LEAD_NOTIFY_EMAIL = env('LEAD_NOTIFY_EMAIL', default='')
LEAD_FORM_THROTTLE = env('LEAD_FORM_THROTTLE', default='5/3600')  # "<count>/<seconds>", used by Module 05
PILOT_REFERRALS_PER_PARTNER = env.int('PILOT_REFERRALS_PER_PARTNER', default=3)  # free referrals before fees (plan §7)
# A page price copied from a partner quote hides itself after this many days (CLAUDE.md invariant 3: dated, sourced prices).
PRICE_MAX_AGE_DAYS = env.int('PRICE_MAX_AGE_DAYS', default=90)

# --- Tracking IDs (Module 06). Blank = tag not rendered. ---
GA4_MEASUREMENT_ID = env('GA4_MEASUREMENT_ID', default='')
GOOGLE_ADS_ID = env('GOOGLE_ADS_ID', default='')
GOOGLE_ADS_FORM_CONVERSION_LABEL = env('GOOGLE_ADS_FORM_CONVERSION_LABEL', default='')
GOOGLE_ADS_WHATSAPP_CONVERSION_LABEL = env('GOOGLE_ADS_WHATSAPP_CONVERSION_LABEL', default='')
GOOGLE_ADS_CALL_CONVERSION_LABEL = env('GOOGLE_ADS_CALL_CONVERSION_LABEL', default='')
GOOGLE_SITE_VERIFICATION = env('GOOGLE_SITE_VERIFICATION', default='')

# Request bodies are never logged; only the console handler, one line per record.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'plain': {'format': '%(asctime)s %(levelname)s %(name)s %(message)s'}},
    'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'plain'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}

# --- Lead form protection (Module 05) ---
LEAD_DUPLICATE_WINDOW_HOURS = env.int('LEAD_DUPLICATE_WINDOW_HOURS', default=24)
# Header that carries the real client IP. Blank = use REMOTE_ADDR.
# For a comma-separated header such as X-Forwarded-For, only the entries APPENDED by our own proxies are trusted:
# the client IP is the CLIENT_IP_TRUSTED_HOPS-th entry from the right (Cloud Run direct = 1; behind a Google
# load balancer = 2). Anything further left was sent by the client and is ignored (docs/deployment.md §2).
CLIENT_IP_HEADER = env('CLIENT_IP_HEADER', default='')
CLIENT_IP_TRUSTED_HOPS = env.int('CLIENT_IP_TRUSTED_HOPS', default=1)
# Throttle counters must be shared by every process that serves the site, with no Redis:
#   file = one host with several Gunicorn workers;  db = Cloud Run (many instances), needs `createcachetable`.
CACHE_BACKEND = env('CACHE_BACKEND', default='file')
if CACHE_BACKEND == 'db':
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.db.DatabaseCache', 'LOCATION': 'django_cache'}}
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': str(Path(tempfile.gettempdir()) / 'travel_platform_cache'),
        }
    }

# Hosts that answer with a 301 to the canonical SITE_BASE_URL host (e.g. www.mytravelplanner.in). Blank = none.
REDIRECT_TO_CANONICAL_HOSTS = env.list('REDIRECT_TO_CANONICAL_HOSTS', default=[])

# --- Admin second factor (Module 07; owner decision 2026-10-25). Always on in production (prod.py). ---
ADMIN_REQUIRE_MFA = env.bool('ADMIN_REQUIRE_MFA', default=False)
OTP_TOTP_ISSUER = SITE_NAME
OTP_ADMIN_HIDE_SENSITIVE_DATA = True  # authenticator secrets are never shown in the admin device list
