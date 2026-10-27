"""Module 07: admin MFA, Cloud Run settings (client IP, cache, canonical host), production image and deploy files."""
import os
import re
import subprocess
import sys
import time
from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice

from .test_foundation import BACKEND_DIR, PROD_ENV
from .throttle import client_ip

REPO_DIR = BACKEND_DIR.parent
DEPLOY_DIR = REPO_DIR / 'deploy'


def current_code(device):
    totp = TOTP(device.bin_key, device.step, device.t0, device.digits, device.drift)
    totp.time = time.time()
    return f'{totp.token():0{device.digits}d}'


def wrong_code(device):
    return f'{(int(current_code(device)) + 500000) % 1000000:06d}'


@override_settings(ADMIN_REQUIRE_MFA=True)
class AdminMfaTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_superuser('owner', 'owner@example.test', 'a-long-test-password')
        self.client.force_login(self.owner)
        self.index = reverse('admin:index')
        self.mfa = reverse('admin:mfa')

    def test_password_alone_does_not_open_the_admin(self):
        response = self.client.get(self.index)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin:login'), response['Location'])
        # ...and the login page sends a password-authenticated user straight to the code step
        login = self.client.get(response['Location'])
        self.assertEqual(login.status_code, 302)
        self.assertTrue(login['Location'].startswith(self.mfa))
        for url in (reverse('admin:core_lead_changelist'), reverse('admin:core_partner_changelist')):
            self.assertEqual(self.client.get(url).status_code, 302, url)

    def test_first_sign_in_enrols_an_authenticator_with_a_qr_code(self):
        response = self.client.get(self.mfa)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertRegex(html, r'<div class="mfa-qr"[^>]*><svg')  # inline QR code, generated on the server
        self.assertNotIn('<?xml', html)
        self.assertIn('class="mfa-secret"', html)
        self.assertIn('Set up two-step sign-in', html)
        device = TOTPDevice.objects.get(user=self.owner)
        self.assertFalse(device.confirmed)
        self.assertIn('no-store', response['Cache-Control'])  # the QR code / secret is never cached

        response = self.client.post(self.mfa, {'token': current_code(device), 'next': self.index})
        self.assertRedirects(response, self.index)
        device.refresh_from_db()
        self.assertTrue(device.confirmed)
        self.assertEqual(self.client.get(self.index).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:core_lead_changelist')).status_code, 200)

    def test_wrong_code_is_refused_and_repeated_failures_are_throttled(self):
        self.client.get(self.mfa)
        device = TOTPDevice.objects.get(user=self.owner)
        response = self.client.post(self.mfa, {'token': wrong_code(device)})
        self.assertContains(response, 'That code is not right')
        response = self.client.post(self.mfa, {'token': wrong_code(device)})
        self.assertContains(response, 'Too many wrong codes')
        device.refresh_from_db()
        self.assertFalse(device.confirmed)
        self.assertEqual(self.client.get(self.index).status_code, 302)

    def test_non_numeric_code_is_a_form_error(self):
        response = self.client.post(self.mfa, {'token': 'abcdef'})
        self.assertContains(response, 'Enter the numbers shown')

    def test_once_enrolled_the_secret_is_never_shown_again(self):
        device = TOTPDevice.objects.create(user=self.owner, name='phone', confirmed=True)
        html = self.client.get(self.mfa).content.decode()
        self.assertNotIn('class="mfa-qr"', html)  # the element, not the CSS rule that styles it
        self.assertNotIn('class="mfa-secret"', html)
        self.assertEqual(TOTPDevice.objects.filter(user=self.owner).count(), 1)  # no second device created
        self.assertRedirects(self.client.post(self.mfa, {'token': current_code(device)}), self.index)

    def test_code_step_needs_a_password_login_first(self):
        self.client.logout()
        response = self.client.get(self.mfa)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin:login'), response['Location'])
        self.assertEqual(TOTPDevice.objects.count(), 0)

    def test_non_staff_user_cannot_enrol(self):
        visitor = get_user_model().objects.create_user('visitor', 'v@example.test', 'a-long-test-password')
        self.client.force_login(visitor)
        self.assertEqual(self.client.get(self.mfa).status_code, 302)
        self.assertFalse(TOTPDevice.objects.filter(user=visitor).exists())

    def test_next_cannot_redirect_off_site(self):
        device = TOTPDevice.objects.create(user=self.owner, name='phone', confirmed=True)
        response = self.client.post(self.mfa, {'token': current_code(device), 'next': 'https://evil.test/'})
        self.assertRedirects(response, self.index)

    def test_logout_is_offered_on_the_code_page(self):
        self.assertContains(self.client.get(self.mfa), f'action="{reverse("admin:logout")}"')

    @override_settings(ADMIN_REQUIRE_MFA=False)
    def test_switch_off_for_local_development(self):
        self.assertEqual(self.client.get(self.index).status_code, 200)
        self.assertRedirects(self.client.get(self.mfa), self.index)

    def test_authenticator_secrets_are_hidden_in_the_admin(self):
        self.assertTrue(settings.OTP_ADMIN_HIDE_SENSITIVE_DATA)
        self.assertEqual(settings.OTP_TOTP_ISSUER, settings.SITE_NAME)


class ResetAdminMfaCommandTests(TestCase):
    def test_removes_every_device_of_that_user_only(self):
        user_model = get_user_model()
        owner = user_model.objects.create_superuser('owner', 'o@example.test', 'a-long-test-password')
        other = user_model.objects.create_superuser('other', 'x@example.test', 'a-long-test-password')
        TOTPDevice.objects.create(user=owner, name='a', confirmed=True)
        TOTPDevice.objects.create(user=owner, name='b', confirmed=False)
        TOTPDevice.objects.create(user=other, name='c', confirmed=True)
        out = StringIO()
        call_command('reset_admin_mfa', 'owner', stdout=out)
        self.assertIn('Removed 2', out.getvalue())
        self.assertFalse(TOTPDevice.objects.filter(user=owner).exists())
        self.assertTrue(TOTPDevice.objects.filter(user=other).exists())

    def test_unknown_user(self):
        with self.assertRaises(CommandError):
            call_command('reset_admin_mfa', 'nobody')


class ClientIpTests(SimpleTestCase):
    def request(self, **meta):
        return RequestFactory().get('/', REMOTE_ADDR='10.0.0.9', **meta)

    @override_settings(CLIENT_IP_HEADER='X-Forwarded-For', CLIENT_IP_TRUSTED_HOPS=1)
    def test_cloud_run_uses_the_entry_google_appended(self):
        self.assertEqual(client_ip(self.request(HTTP_X_FORWARDED_FOR='203.0.113.7')), '203.0.113.7')
        # A client that sends its own X-Forwarded-For cannot choose its throttle bucket.
        spoofed = self.request(HTTP_X_FORWARDED_FOR='1.2.3.4, 5.6.7.8, 203.0.113.7')
        self.assertEqual(client_ip(spoofed), '203.0.113.7')

    @override_settings(CLIENT_IP_HEADER='X-Forwarded-For', CLIENT_IP_TRUSTED_HOPS=2)
    def test_behind_a_load_balancer_skips_the_balancer_entry(self):
        request = self.request(HTTP_X_FORWARDED_FOR='1.2.3.4,203.0.113.7,34.120.0.1')
        self.assertEqual(client_ip(request), '203.0.113.7')
        self.assertEqual(client_ip(self.request(HTTP_X_FORWARDED_FOR='34.120.0.1')), '10.0.0.9')  # too short

    @override_settings(CLIENT_IP_HEADER='X-Forwarded-For', CLIENT_IP_TRUSTED_HOPS=2)
    def test_behind_the_nginx_edge_uses_the_address_nginx_wrote(self):
        # nginx overwrites X-Forwarded-For with its peer, then Google appends the edge VM's address.
        self.assertEqual(client_ip(self.request(HTTP_X_FORWARDED_FOR='203.0.113.7, 34.14.158.50')), '203.0.113.7')

    @override_settings(CLIENT_IP_HEADER='X-Real-IP')
    def test_single_value_header_and_fallback(self):
        self.assertEqual(client_ip(self.request(HTTP_X_REAL_IP='198.51.100.2')), '198.51.100.2')
        self.assertEqual(client_ip(self.request()), '10.0.0.9')

    @override_settings(CLIENT_IP_HEADER='')
    def test_no_header_configured_ignores_forwarded_headers(self):
        self.assertEqual(client_ip(self.request(HTTP_X_FORWARDED_FOR='1.2.3.4')), '10.0.0.9')


@override_settings(SITE_BASE_URL='https://mytravelplanner.in', REDIRECT_TO_CANONICAL_HOSTS=['www.mytravelplanner.in'],
                   ALLOWED_HOSTS=['mytravelplanner.in', 'www.mytravelplanner.in', 'travel-web-x.a.run.app'])
class CanonicalHostTests(TestCase):
    def test_www_redirects_permanently_to_the_same_path_keeping_click_ids(self):
        response = self.client.get('/contact/?gclid=abc&utm_source=g', HTTP_HOST='www.mytravelplanner.in')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://mytravelplanner.in/contact/?gclid=abc&utm_source=g')

    def test_canonical_and_run_app_hosts_are_served(self):
        for host in ('mytravelplanner.in', 'travel-web-x.a.run.app'):
            self.assertEqual(self.client.get('/', HTTP_HOST=host).status_code, 200, host)

    def test_health_is_never_redirected(self):
        self.assertEqual(self.client.get('/health/', HTTP_HOST='www.mytravelplanner.in').status_code, 200)

    @override_settings(REDIRECT_TO_CANONICAL_HOSTS=[])
    def test_nothing_redirects_when_unset(self):
        self.assertEqual(self.client.get('/', HTTP_HOST='www.mytravelplanner.in').status_code, 200)


EDGE_KEY = 'a1' * 32


@override_settings(EDGE_SHARED_SECRET=EDGE_KEY, ALLOWED_HOSTS=['mytravelplanner.in', 'travel-web-x.a.run.app'])
class EdgeSecretTests(TestCase):
    def test_direct_requests_to_run_app_are_refused(self):
        for headers in ({}, {'HTTP_X_TRAVEL_EDGE_KEY': 'wrong'}, {'HTTP_X_TRAVEL_EDGE_KEY': ''}):
            response = self.client.get('/', HTTP_HOST='travel-web-x.a.run.app', **headers)
            self.assertEqual(response.status_code, 403, headers)
        # the lead form too: a POST cannot reach the throttle or the database without the key
        self.assertEqual(self.client.post(reverse('core:enquiry'), {}, HTTP_HOST='travel-web-x.a.run.app').status_code, 403)

    def test_requests_through_the_edge_are_served(self):
        response = self.client.get('/', HTTP_HOST='mytravelplanner.in', HTTP_X_TRAVEL_EDGE_KEY=EDGE_KEY)
        self.assertEqual(response.status_code, 200)

    def test_health_stays_open_for_probes(self):
        self.assertEqual(self.client.get('/health/', HTTP_HOST='travel-web-x.a.run.app').status_code, 200)

    @override_settings(EDGE_SHARED_SECRET='')
    def test_blank_secret_turns_the_check_off(self):
        self.assertEqual(self.client.get('/', HTTP_HOST='mytravelplanner.in').status_code, 200)

    def test_runs_before_everything_else(self):
        self.assertEqual(settings.MIDDLEWARE[0], 'apps.core.middleware.EdgeSecretMiddleware')


@override_settings(USE_X_FORWARDED_HOST=True, ALLOWED_HOSTS=['mytravelplanner.in', 'travel-web-x.a.run.app'])
class ForwardedHostTests(SimpleTestCase):
    def test_public_host_comes_from_the_edge(self):
        request = RequestFactory().get('/', HTTP_HOST='travel-web-x.a.run.app', HTTP_X_FORWARDED_HOST='mytravelplanner.in')
        self.assertEqual(request.get_host(), 'mytravelplanner.in')

    def test_forwarded_host_is_still_checked_against_allowed_hosts(self):
        from django.core.exceptions import DisallowedHost
        request = RequestFactory().get('/', HTTP_HOST='travel-web-x.a.run.app', HTTP_X_FORWARDED_HOST='evil.example')
        with self.assertRaises(DisallowedHost):
            request.get_host()


def prod_settings(code, **overrides):
    """Run `code` after importing config.settings.prod as `p`, in a clean interpreter with a valid prod env."""
    skip = set(PROD_ENV) | {'DEBUG', 'ADMIN_URL_PATH', 'ADMIN_REQUIRE_MFA', 'CACHE_BACKEND'}
    env = {k: v for k, v in os.environ.items() if k not in skip}
    env.update(PROD_ENV)
    env.update(overrides)
    return subprocess.run([sys.executable, '-c', f'import config.settings.prod as p; {code}'],
                          cwd=BACKEND_DIR, env=env, capture_output=True, text=True)


class ProductionSettingsTests(SimpleTestCase):
    def test_mfa_is_forced_on(self):
        result = prod_settings('print(p.ADMIN_REQUIRE_MFA)')
        self.assertEqual(result.stdout.strip(), 'True', result.stderr)

    def test_refuses_mfa_switched_off(self):
        result = prod_settings('', ADMIN_REQUIRE_MFA='False')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ADMIN_REQUIRE_MFA', result.stderr)

    def test_refuses_the_default_admin_path(self):
        result = prod_settings('', ADMIN_URL_PATH='admin/')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ADMIN_URL_PATH', result.stderr)

    def test_refuses_an_unknown_cache_backend(self):
        result = prod_settings('', CACHE_BACKEND='redis')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('CACHE_BACKEND', result.stderr)

    def test_cloud_run_uses_the_database_cache(self):
        result = prod_settings("print(p.CACHES['default']['BACKEND'])", CACHE_BACKEND='db')
        self.assertEqual(result.stdout.strip(), 'django.core.cache.backends.db.DatabaseCache', result.stderr)

    def test_otp_middleware_runs_after_authentication(self):
        middleware = settings.MIDDLEWARE
        self.assertLess(middleware.index('django.contrib.auth.middleware.AuthenticationMiddleware'),
                        middleware.index('django_otp.middleware.OTPMiddleware'))
        self.assertIn('config.apps.MfaAdminConfig', settings.INSTALLED_APPS)
        self.assertNotIn('django.contrib.admin', settings.INSTALLED_APPS)


class ProductionImageTests(SimpleTestCase):
    def setUp(self):
        self.dockerfile = (BACKEND_DIR / 'Dockerfile.prod').read_text(encoding='utf-8')

    def test_installs_production_requirements_only(self):
        self.assertIn('pip install -r requirements/prod.txt', self.dockerfile)
        self.assertNotIn('dev.txt', self.dockerfile)
        prod = (BACKEND_DIR / 'requirements' / 'prod.txt').read_text(encoding='utf-8')
        self.assertNotIn('dev.txt', prod)
        base = (BACKEND_DIR / 'requirements' / 'base.txt').read_text(encoding='utf-8')
        self.assertIn('django-otp', base)
        self.assertNotIn('Pillow', base)

    def test_runs_as_non_root_with_prod_settings_on_the_cloud_run_port(self):
        self.assertRegex(self.dockerfile, r'\nUSER app\n')
        self.assertIn('DJANGO_SETTINGS_MODULE=config.settings.prod', self.dockerfile)
        self.assertIn('--bind ":${PORT}"', self.dockerfile)
        self.assertIn('collectstatic --noinput', self.dockerfile)

    def test_secrets_never_enter_the_image(self):
        ignore = (BACKEND_DIR / '.dockerignore').read_text(encoding='utf-8').split()
        self.assertIn('.env', ignore)
        self.assertNotRegex(self.dockerfile, r'SECRET_KEY=(?!collectstatic-only)')
        self.assertIn('#!include:.dockerignore', (BACKEND_DIR / '.gcloudignore').read_text(encoding='utf-8'))


class DeployFilesTests(SimpleTestCase):
    def setUp(self):
        if not DEPLOY_DIR.is_dir():
            self.skipTest('deploy/ is not mounted (see docker-compose.yml)')
        self.env_example = (DEPLOY_DIR / 'cloudrun' / 'env.prod.yaml.example').read_text(encoding='utf-8')
        self.script = (DEPLOY_DIR / 'cloudrun' / 'deploy.sh').read_text(encoding='utf-8')

    def env_keys(self):
        return re.findall(r'^([A-Z][A-Z0-9_]+):', self.env_example, re.M)

    def test_env_template_has_no_secrets(self):
        keys = self.env_keys()
        for secret in ('SECRET_KEY', 'DB_PASSWORD', 'EMAIL_HOST_PASSWORD', 'POSTGRES_ADMIN_PASSWORD'):
            self.assertNotIn(secret, keys)
        for secret in ('SECRET_KEY=travel-secret-key', 'DB_PASSWORD=travel-db-password'):
            self.assertIn(secret, self.script)  # from Secret Manager instead

    def test_env_template_is_set_up_for_cloud_run(self):
        values = dict(re.findall(r'^([A-Z][A-Z0-9_]+):\s*"([^"]*)"', self.env_example, re.M))
        self.assertEqual(values['DJANGO_SETTINGS_MODULE'], 'config.settings.prod')
        self.assertEqual(values['CACHE_BACKEND'], 'db')
        self.assertEqual(values['CLIENT_IP_HEADER'], 'X-Forwarded-For')
        self.assertEqual(values['SITE_BASE_URL'], 'https://mytravelplanner.in')
        self.assertEqual(values['REDIRECT_TO_CANONICAL_HOSTS'], 'www.mytravelplanner.in')
        self.assertNotEqual(values['ADMIN_URL_PATH'], 'admin/')
        self.assertTrue(values['DB_HOST'].startswith('/cloudsql/'))

    def test_every_template_key_is_a_real_setting(self):
        settings_src = ''.join(p.read_text(encoding='utf-8') for p in (BACKEND_DIR / 'config' / 'settings').glob('*.py'))
        for key in self.env_keys():
            if key == 'DJANGO_SETTINGS_MODULE':
                continue
            self.assertRegex(settings_src, r"env(\.\w+)?\('" + key + "'", f'{key} is not read by the settings')

    def test_release_order_is_migrate_before_deploy(self):
        self.assertIn('release) build; migrate; deploy_service ;;', self.script)
        self.assertIn('createcachetable', self.script)
        self.assertIn('placeholders', self.script)  # refuses an unfilled env file

    def test_never_deploys_into_the_pglive_projects(self):
        self.assertIn('pglive-*', self.script)
        self.assertNotIn('sql instances patch', self.script)  # the shared instance's settings belong to PGLive

    def test_shared_instance_role_is_capped_and_not_a_cloudsql_superuser(self):
        sql = (DEPLOY_DIR / 'cloudsql' / 'create-travel-db.sql').read_text(encoding='utf-8')
        self.assertIn('CONNECTION LIMIT 12', sql)
        self.assertIn('NOCREATEROLE', sql)
        self.assertIn('REVOKE ALL ON DATABASE travel_platform FROM PUBLIC', sql)
        self.assertNotIn('pg_platform', sql)  # never touches PGLive's database
        self.assertNotIn('gcloud sql users create', self.script)  # that adds cloudsqlsuperuser

    def test_edge_config_only_adds_its_own_server_blocks(self):
        conf = (DEPLOY_DIR / 'edge' / 'travel.conf.template').read_text(encoding='utf-8')
        self.assertNotIn('default_server', conf)
        self.assertNotRegex(conf, r'pglive_|\$upstream_host|pglive-tls')  # none of PGLive's zones, variables or snippets
        self.assertIn('proxy_set_header X-Forwarded-For $remote_addr;', conf)
        self.assertIn('include /etc/nginx/travel-edge-key.conf;', conf)
        setup = (DEPLOY_DIR / 'edge' / 'setup-travel-edge.sh').read_text(encoding='utf-8')
        self.assertIn('nginx -t', setup)
        self.assertNotRegex(setup, r'>\s*/etc/nginx/conf\.d/(?!travel)')  # writes only travel* files

    def test_backups_are_encrypted_on_the_fly_and_restore_prints_no_personal_data(self):
        download = (DEPLOY_DIR / 'backup' / 'download_backup.sh').read_text(encoding='utf-8')
        self.assertIn('| gpg --symmetric', download)
        self.assertNotRegex(download, r'pg_dump[^|]*>\s*\S+\.dump\b')  # never a plain .dump file on disk
        restore = (DEPLOY_DIR / 'backup' / 'restore_check.sh').read_text(encoding='utf-8')
        self.assertIn('DROP DATABASE IF EXISTS', restore)
        queries = restore.split('==> Row counts')[1].lower()  # everything the script runs after restoring
        for column in ('phone', 'name,', 'email'):
            self.assertNotIn(column, queries)
