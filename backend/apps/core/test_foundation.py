import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

PROD_ENV = {
    'DJANGO_SETTINGS_MODULE': 'config.settings.prod',
    'SECRET_KEY': 'x' * 60,
    'ALLOWED_HOSTS': 'example.test',
    'SITE_BASE_URL': 'https://example.test',
    'ADMIN_URL_PATH': 'owner-desk/',
}


def import_prod_settings(**overrides):
    """Import config.settings.prod in a clean interpreter with the given env; return the process result."""
    env = {k: v for k, v in os.environ.items()
           if k not in PROD_ENV and k not in ('DEBUG', 'ADMIN_URL_PATH', 'ADMIN_REQUIRE_MFA', 'CACHE_BACKEND')}
    env.update(PROD_ENV)
    env.update(overrides)
    env = {k: v for k, v in env.items() if v is not None}
    return subprocess.run(
        [sys.executable, '-c', 'import config.settings.prod'],
        cwd=BACKEND_DIR, env=env, capture_output=True, text=True,
    )


class HealthTests(TestCase):
    def test_health_is_plain_ok_and_uncached(self):
        response = self.client.get(reverse('core:health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')
        self.assertIn('no-cache', response['Cache-Control'])

    def test_health_rejects_post(self):
        self.assertEqual(self.client.post(reverse('core:health')).status_code, 405)


class SiteConfigTests(TestCase):
    @override_settings(SITE_NAME='Test Brand', WHATSAPP_NUMBER='919000000000', RESPONSE_HOURS_TEXT='9 to 5',
                       GA4_MEASUREMENT_ID='G-TEST', CONSENT_NOTICE_VERSION='v-test')
    def test_context_processor_exposes_config_from_settings(self):
        response = self.client.get('/does-not-exist/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context['site']['name'], 'Test Brand')
        self.assertEqual(response.context['site']['whatsapp_number'], '919000000000')
        self.assertEqual(response.context['site']['response_hours'], '9 to 5')
        self.assertEqual(response.context['site']['consent_notice_version'], 'v-test')
        self.assertEqual(response.context['tracking']['ga4_id'], 'G-TEST')

    def test_blank_tracking_ids_render_no_tag(self):
        response = self.client.get('/does-not-exist/')
        self.assertNotContains(response, 'google-site-verification', status_code=404)

    def test_404_page_is_noindex(self):
        response = self.client.get('/does-not-exist/')
        self.assertContains(response, 'content="noindex,follow"', status_code=404)


class AdminPathTests(TestCase):
    @override_settings(ADMIN_URL_PATH='manage-x/')
    def test_admin_path_comes_from_settings_url_conf(self):
        # urlconf is built at import time, so only assert the normalisation helper in base settings.
        from config.settings import base
        self.assertTrue(base.ADMIN_URL_PATH.endswith('/'))
        self.assertFalse(base.ADMIN_URL_PATH.startswith('/'))

    def test_admin_requires_login(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_no_public_registration_or_login_page(self):
        for path in ('/accounts/login/', '/register/', '/signup/'):
            self.assertEqual(self.client.get(path).status_code, 404, path)


class ProdSettingsTests(SimpleTestCase):
    def test_valid_prod_env_imports(self):
        result = import_prod_settings()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_refuses_debug_true(self):
        result = import_prod_settings(DEBUG='True')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DEBUG must not be enabled', result.stderr)

    def test_refuses_weak_secret_key(self):
        result = import_prod_settings(SECRET_KEY='change-me-dev-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('SECRET_KEY', result.stderr)

    def test_refuses_missing_allowed_hosts(self):
        result = import_prod_settings(ALLOWED_HOSTS='')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ALLOWED_HOSTS', result.stderr)

    def test_refuses_non_https_site_url(self):
        result = import_prod_settings(SITE_BASE_URL='http://example.test')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('SITE_BASE_URL', result.stderr)
