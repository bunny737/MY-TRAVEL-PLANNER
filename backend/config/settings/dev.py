from .base import *  # noqa: F401,F403
from .base import INSTALLED_APPS, MIDDLEWARE, STORAGES, env

DEBUG = env.bool('DEBUG', default=True)

# runserver serves static files itself; WhiteNoise would only warn about the missing staticfiles/ dir.
MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m]

# Dev tooling only (ERD via graph_models); not shipped to prod.
INSTALLED_APPS = INSTALLED_APPS + ['django_extensions']

# No collectstatic needed locally: skip the manifest.
STORAGES = {**STORAGES, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}}
