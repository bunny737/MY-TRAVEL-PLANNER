import logging
from datetime import date, timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .attribution import ATTRIBUTION_SESSION_KEY
from .models import Lead, Partner
from .views import CONVERSION_PENDING

LOCMEM = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

VALID = {
    'name': 'Asha Rao',
    'phone': '98765 43210',
    'service_type': 'tour',
    'travel_date_or_month': 'mid December',
    'travellers': '4',
    'pickup_city': 'Hyderabad',
    'budget': 'around 20,000',
    'notes': 'Two children',
    'consent_given': 'on',  # required on the form (owner decision 2026-10-25)
}


def make_lead(**overrides):
    data = dict(name='Asha Rao', phone='9876543210', service_type='tour', travel_date_or_month='Dec', travellers=4)
    data.update(overrides)
    return Lead.objects.create(**data)


def make_partner(**overrides):
    data = dict(business_name='Hill Cabs', phone='9000000001', offers_tours=True,
                referral_terms_agreed_on=date(2026, 10, 28))
    data.update(overrides)
    return Partner.objects.create(**data)


@override_settings(CACHES=LOCMEM, LEAD_FORM_THROTTLE='100/3600', LEAD_NOTIFY_EMAIL='')
class FormTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def post(self, **overrides):
        data = {**VALID, **overrides}
        return self.client.post(reverse('core:enquiry'), data)


class EnquiryFormRenderTests(FormTestCase):
    def test_get_shows_form_with_unchecked_consent_and_no_referral_paragraph(self):
        response = self.client.get(reverse('core:enquiry'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('name="consent_given"', html)
        self.assertNotRegex(html, r'name="consent_given"[^>]*checked')
        self.assertIn('may share my name, phone number and trip details with one selected independent travel partner', html)
        self.assertNotIn('We are a travel enquiry and referral platform', html)
        self.assertIn('share my name, phone number and trip details with one selected', html)
        self.assertIn('csrfmiddlewaretoken', html)

    def test_form_page_is_noindex(self):
        self.assertContains(self.client.get(reverse('core:enquiry')), 'content="noindex,follow"')

    def test_form_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(reverse('core:enquiry'), VALID).status_code, 403)
        self.assertEqual(Lead.objects.count(), 0)


class RequiredFieldsTests(FormTestCase):
    def test_valid_submission_saves_normalised_lead_and_redirects(self):
        response = self.post()
        self.assertRedirects(response, reverse('core:thank_you'))
        lead = Lead.objects.get()
        self.assertEqual(lead.phone, '+919876543210')
        self.assertEqual(lead.service_type, 'tour')
        self.assertEqual(lead.travellers, 4)
        self.assertEqual(lead.lead_channel, 'form')
        self.assertEqual(lead.status, 'new')

    def test_each_required_field_is_enforced(self):
        for field in ('name', 'phone', 'service_type', 'travel_date_or_month', 'travellers'):
            response = self.post(**{field: ''})
            self.assertEqual(response.status_code, 200, field)
            self.assertIn(field, response.context['form'].errors, field)
        self.assertEqual(Lead.objects.count(), 0)

    def test_optional_fields_may_be_blank(self):
        self.post(pickup_city='', budget='', notes='')
        self.assertEqual(Lead.objects.count(), 1)

    def test_phone_and_traveller_count_validated_on_the_server(self):
        for overrides in ({'phone': '12345'}, {'travellers': '0'}, {'travellers': '101'}, {'travellers': 'many'},
                          {'service_type': 'helicopter'}):
            self.post(**overrides)
        self.assertEqual(Lead.objects.count(), 0)

    def test_overlong_notes_rejected(self):
        self.post(notes='x' * 1001)
        self.assertEqual(Lead.objects.count(), 0)

    def test_invalid_form_does_not_set_conversion_flag(self):
        self.post(phone='12345')
        self.assertNotIn(CONVERSION_PENDING, self.client.session)


class ConsentTests(FormTestCase):
    def test_without_the_tick_nothing_is_saved_and_the_box_shows_why(self):
        data = {k: v for k, v in VALID.items() if k != 'consent_given'}
        response = self.client.post(reverse('core:enquiry'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)
        self.assertIn('consent_given', response.context['form'].errors)
        self.assertContains(response, 'Please tick this box so we can pass your enquiry to a local partner')
        self.assertContains(response, 'aria-invalid="true"')
        self.assertNotIn(CONVERSION_PENDING, self.client.session)

    def test_an_explicit_no_is_refused_too(self):
        self.post(consent_given='')
        self.assertEqual(Lead.objects.count(), 0)

    def test_checkbox_is_required_but_never_pre_ticked(self):
        html = self.client.get(reverse('core:enquiry')).content.decode()
        tag = html[html.index('name="consent_given"') - 30:html.index('name="consent_given"') + 200]
        self.assertIn('required', tag)
        self.assertNotIn('checked', tag)
        self.assertIn('(required)', html)

    @override_settings(CONSENT_NOTICE_VERSION='2026-10-v9')
    def test_checkbox_records_time_notice_version_and_source(self):
        before = timezone.now()
        self.post(consent_given='on')
        lead = Lead.objects.get()
        self.assertTrue(lead.consent_given)
        self.assertGreaterEqual(lead.consent_at, before)
        self.assertEqual(lead.consent_notice_version, '2026-10-v9')
        self.assertEqual(lead.consent_source, 'form')

    def test_lead_without_consent_cannot_be_assigned_a_partner(self):
        lead = make_lead()
        lead.partner = make_partner()
        with self.assertRaises(ValidationError):
            lead.save()
        with self.assertRaises(ValidationError):
            lead.full_clean()
        lead.refresh_from_db()
        self.assertIsNone(lead.partner)

    def test_thank_you_confirms_the_agreed_referral_and_does_not_promise_to_ask_again(self):
        self.post()
        response = self.client.get(reverse('core:thank_you'))
        self.assertContains(response, 'as you agreed')
        self.assertNotContains(response, 'ask for your permission')


class StatusLifecycleTests(TestCase):
    def test_new_is_default_and_has_no_stamps(self):
        lead = make_lead()
        self.assertEqual(lead.status, Lead.Status.NEW)
        self.assertIsNone(lead.qualified_at)
        self.assertIsNone(lead.referred_at)
        self.assertIsNone(lead.partner_responded_at)

    def test_status_values_are_exactly_the_planned_enum(self):
        self.assertEqual(
            [value for value, _ in Lead.Status.choices],
            ['new', 'qualified', 'referred', 'partner_responded', 'won', 'lost', 'spam', 'invalid', 'withdrawn'],
        )

    def test_transitions_stamp_once_and_never_overwrite(self):
        lead = make_lead()
        for status, field in (('qualified', 'qualified_at'), ('partner_responded', 'partner_responded_at')):
            lead.status = status
            lead.save()
            first = getattr(lead, field)
            self.assertIsNotNone(first, field)
            lead.status = 'won'
            lead.save()
            lead.status = status
            lead.save()
            self.assertEqual(getattr(lead, field), first, field)

    def test_assigning_partner_moves_to_referred_and_stamps(self):
        lead = make_lead(consent_given=True, consent_source='manual')
        lead.partner = make_partner()
        lead.save()
        lead.refresh_from_db()
        self.assertEqual(lead.status, Lead.Status.REFERRED)
        self.assertIsNotNone(lead.referred_at)

    def test_assigning_from_qualified_keeps_the_earlier_stamp(self):
        lead = make_lead(consent_given=True, consent_source='manual', status='qualified')
        qualified_at = lead.qualified_at
        lead.partner = make_partner()
        lead.save()
        self.assertEqual(lead.qualified_at, qualified_at)
        self.assertEqual(lead.status, 'referred')


class PartnerAssignmentTests(TestCase):
    def setUp(self):
        self.lead = make_lead(consent_given=True, consent_source='whatsapp_reply')

    def test_consented_lead_can_go_to_ready_partner(self):
        self.lead.partner = make_partner()
        self.lead.save()
        self.assertEqual(self.lead.status, 'referred')

    def test_inactive_partner_rejected(self):
        self.lead.partner = make_partner(is_active=False)
        with self.assertRaises(ValidationError):
            self.lead.save()

    def test_partner_without_recorded_terms_rejected(self):
        self.lead.partner = make_partner(referral_terms_agreed_on=None)
        with self.assertRaises(ValidationError):
            self.lead.save()

    def test_spam_invalid_and_withdrawn_leads_cannot_be_referred(self):
        partner = make_partner()
        for status in ('spam', 'invalid', 'withdrawn'):
            lead = make_lead(consent_given=True, consent_source='manual', status=status)
            lead.partner = partner
            with self.assertRaises(ValidationError, msg=status):
                lead.save()

    def test_later_edits_do_not_revalidate_an_existing_assignment(self):
        partner = make_partner()
        self.lead.partner = partner
        self.lead.save()
        partner.is_active = False
        partner.save()
        lead = Lead.objects.get(pk=self.lead.pk)
        lead.status = 'won'
        lead.founder_notes = 'Booked'
        lead.save()  # must not raise although the partner has since been deactivated
        self.assertEqual(Lead.objects.get(pk=lead.pk).status, 'won')

    def test_partner_with_leads_cannot_be_deleted(self):
        partner = make_partner()
        self.lead.partner = partner
        self.lead.save()
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            partner.delete()

    def test_consent_source_required_when_consent_given(self):
        lead = Lead(name='A', phone='9876543210', service_type='cab', travel_date_or_month='Nov', travellers=2,
                    consent_given=True)
        with self.assertRaises(ValidationError) as ctx:
            lead.full_clean()
        self.assertIn('consent_source', ctx.exception.message_dict)


@override_settings(CACHES=LOCMEM, LEAD_NOTIFY_EMAIL='')
class ThrottleAndHoneypotTests(TestCase):
    def setUp(self):
        cache.clear()

    @override_settings(LEAD_FORM_THROTTLE='2/60')
    def test_throttle_blocks_after_limit_and_saves_nothing(self):
        for i in range(2):
            self.client.post(reverse('core:enquiry'), {**VALID, 'phone': f'98765432{i}0'})
        self.assertEqual(Lead.objects.count(), 2)
        response = self.client.post(reverse('core:enquiry'), {**VALID, 'phone': '9876543299'})
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, 'try again a little later', status_code=429)
        self.assertEqual(Lead.objects.count(), 2)

    @override_settings(LEAD_FORM_THROTTLE='1/60')
    def test_throttle_is_per_client_ip(self):
        self.client.post(reverse('core:enquiry'), VALID, REMOTE_ADDR='10.0.0.1')
        blocked = self.client.post(reverse('core:enquiry'), {**VALID, 'phone': '9876543299'}, REMOTE_ADDR='10.0.0.1')
        other = self.client.post(reverse('core:enquiry'), {**VALID, 'phone': '9876543288'}, REMOTE_ADDR='10.0.0.2')
        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(other.status_code, 302)

    @override_settings(LEAD_FORM_THROTTLE='1/60', CLIENT_IP_HEADER='X-Real-IP')
    def test_configured_proxy_header_is_used_and_x_forwarded_for_is_ignored(self):
        url = reverse('core:enquiry')
        self.client.post(url, VALID, HTTP_X_REAL_IP='1.1.1.1', HTTP_X_FORWARDED_FOR='9.9.9.1')
        # A spoofed X-Forwarded-For must not buy a fresh budget.
        spoof = self.client.post(url, {**VALID, 'phone': '9876543299'}, HTTP_X_REAL_IP='1.1.1.1',
                                 HTTP_X_FORWARDED_FOR='9.9.9.2')
        self.assertEqual(spoof.status_code, 429)

    def test_bad_throttle_setting_falls_back_to_default(self):
        from .throttle import parse_rate
        for bad in ('', 'abc', '0/60', '5/0', None):
            self.assertEqual(parse_rate(bad), (5, 3600), bad)
        self.assertEqual(parse_rate('3/10'), (3, 10))

    def test_honeypot_saves_nothing_fires_no_conversion_and_looks_like_success(self):
        response = self.client.post(reverse('core:enquiry'), {**VALID, 'website': 'http://spam.example'})
        self.assertRedirects(response, reverse('core:thank_you'))
        self.assertEqual(Lead.objects.count(), 0)
        self.assertNotIn(CONVERSION_PENDING, self.client.session)
        self.assertEqual(len(mail.outbox), 0)


class DuplicateTests(FormTestCase):
    def test_second_submission_is_flagged_saved_and_not_counted(self):
        self.post()
        first_flag = self.client.session.get(CONVERSION_PENDING)
        self.assertTrue(first_flag)
        self.client.cookies.clear()
        self.post(phone='+91 98765-43210')  # same number, different formatting
        self.assertEqual(Lead.objects.count(), 2)
        first, second = Lead.objects.order_by('id')
        self.assertFalse(first.is_duplicate)
        self.assertTrue(second.is_duplicate)
        self.assertNotIn(CONVERSION_PENDING, self.client.session)

    def test_same_phone_different_service_is_not_a_duplicate(self):
        self.post()
        self.post(service_type='cab')
        self.assertFalse(Lead.objects.get(service_type='cab').is_duplicate)

    @override_settings(LEAD_DUPLICATE_WINDOW_HOURS=24)
    def test_outside_the_window_is_not_a_duplicate(self):
        old = make_lead(phone='9876543210')
        Lead.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(hours=25))
        self.post()
        self.assertFalse(Lead.objects.exclude(pk=old.pk).get().is_duplicate)

    def test_spam_originals_do_not_make_later_leads_duplicates(self):
        make_lead(phone='9876543210', status='spam')
        self.post()
        self.assertFalse(Lead.objects.exclude(status='spam').get().is_duplicate)

    def test_conversion_flag_set_once_per_new_lead(self):
        self.post()
        self.assertTrue(self.client.session[CONVERSION_PENDING])
        self.assertEqual(Lead.objects.count(), 1)


class NotificationTests(FormTestCase):
    @override_settings(LEAD_NOTIFY_EMAIL='founder@example.test', SITE_BASE_URL='https://example.test')
    def test_email_has_name_and_admin_link_but_no_phone_or_notes(self):
        self.post()
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['founder@example.test'])
        lead = Lead.objects.get()
        self.assertIn('Asha Rao', message.body)
        self.assertIn(f'https://example.test/admin/core/lead/{lead.pk}/change/', message.body)
        for secret in ('98765', '9876543210', 'Two children', 'Hyderabad'):
            self.assertNotIn(secret, message.subject + message.body)

    def test_no_email_when_not_configured(self):
        self.post()
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(LEAD_NOTIFY_EMAIL='founder@example.test')
    def test_duplicate_does_not_notify_again(self):
        self.post()
        self.client.cookies.clear()
        self.post()
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(LEAD_NOTIFY_EMAIL='founder@example.test')
    def test_mail_failure_never_loses_the_lead(self):
        with mock.patch('apps.core.notifications.send_mail', side_effect=OSError('smtp down')):
            response = self.post()
        self.assertRedirects(response, reverse('core:thank_you'))
        self.assertEqual(Lead.objects.count(), 1)


class AttributionTests(FormTestCase):
    def test_session_attribution_is_copied_to_the_lead(self):
        session = self.client.session
        session[ATTRIBUTION_SESSION_KEY] = {
            'landing_path': '/araku-tour-packages/', 'utm_source': 'google', 'utm_medium': 'cpc',
            'utm_campaign': 'Araku | Search', 'gclid': 'abc123',
        }
        session.save()
        self.post()
        lead = Lead.objects.get()
        self.assertEqual(
            (lead.landing_path, lead.utm_source, lead.utm_medium, lead.utm_campaign, lead.gclid),
            ('/araku-tour-packages/', 'google', 'cpc', 'Araku | Search', 'abc123'),
        )

    def test_missing_attribution_never_blocks_a_lead(self):
        self.post()
        lead = Lead.objects.get()
        self.assertEqual((lead.landing_path, lead.utm_source, lead.gclid), ('', '', ''))

    def test_overlong_attribution_values_are_truncated_not_rejected(self):
        session = self.client.session
        session[ATTRIBUTION_SESSION_KEY] = {'utm_campaign': 'c' * 500, 'gclid': 'g' * 900}
        session.save()
        self.post()
        lead = Lead.objects.get()
        self.assertEqual(len(lead.utm_campaign), 100)
        self.assertEqual(len(lead.gclid), 255)


class PrivacyTests(FormTestCase):
    def test_no_public_route_returns_lead_data(self):
        lead = make_lead(name='Zed Zebra', phone='9123456789')
        for path in ('/leads/', f'/leads/{lead.pk}/', f'/enquiry/{lead.pk}/', '/api/leads/', '/enquiries/'):
            self.assertEqual(self.client.get(path).status_code, 404, path)
        for name in ('core:enquiry', 'core:thank_you', 'core:contact'):
            html = self.client.get(reverse(name)).content.decode()
            self.assertNotIn('Zed Zebra', html)
            self.assertNotIn('9123456789', html)

    def test_thank_you_url_carries_no_identifier_and_page_has_no_personal_data(self):
        response = self.post()
        self.assertEqual(response['Location'], '/thank-you/')
        page = self.client.get('/thank-you/').content.decode()
        for private in ('Asha Rao', '98765', '9876543210', 'Hyderabad', 'Two children'):
            self.assertNotIn(private, page)

    def test_thank_you_is_noindex_and_not_cached(self):
        response = self.client.get(reverse('core:thank_you'))
        self.assertContains(response, 'content="noindex,nofollow"')
        self.assertIn('no-cache', response['Cache-Control'])

    def test_session_stores_only_booleans(self):
        self.post()
        self.assertIs(self.client.session[CONVERSION_PENDING], True)
        stored = str(dict(self.client.session))
        for private in ('Asha', '98765', '9876543210', 'Hyderabad'):
            self.assertNotIn(private, stored)

    def test_personal_details_are_not_written_to_logs(self):
        records = []

        class Capture(logging.Handler):
            def emit(self, record):
                records.append(record.getMessage())

        handler = Capture(level=logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(handler)
        try:
            self.post(phone='9876501234', name='Logcheck Person', notes='secret-note-xyz')
            self.post(phone='bad')
        finally:
            root.removeHandler(handler)
        joined = ' '.join(records)
        for private in ('9876501234', 'Logcheck Person', 'secret-note-xyz'):
            self.assertNotIn(private, joined)


class LeadAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser('owner', 'o@example.test', 'a-long-test-password-1')

    def setUp(self):
        self.client.force_login(self.owner)

    def test_requires_login(self):
        self.client.logout()
        for name in ('admin:core_lead_changelist', 'admin:core_lead_add'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 302, name)

    def test_changelist_filters_and_search(self):
        make_lead(name='Alpha', phone='9111111111')
        make_lead(name='Beta', phone='9222222222', status='qualified')
        url = reverse('admin:core_lead_changelist')
        filtered = self.client.get(url, {'status__exact': 'qualified'})
        self.assertContains(filtered, 'Beta')
        self.assertNotContains(filtered, 'Alpha')
        self.assertContains(self.client.get(url, {'q': '9111111111'}), 'Alpha')

    def test_mark_qualified_action_stamps_only_new_leads(self):
        new = make_lead(name='Newbie')
        referred = make_lead(name='Already', phone='9333333333', consent_given=True, consent_source='manual')
        referred.partner = make_partner()
        referred.save()
        self.client.post(reverse('admin:core_lead_changelist'), {
            'action': 'mark_qualified', '_selected_action': [new.pk, referred.pk],
        })
        new.refresh_from_db()
        referred.refresh_from_db()
        self.assertEqual(new.status, 'qualified')
        self.assertIsNotNone(new.qualified_at)
        self.assertEqual(referred.status, 'referred')

    def test_mark_spam_and_invalid_actions(self):
        spam, invalid, won = make_lead(name='S'), make_lead(name='I', phone='9444444444'), \
            make_lead(name='W', phone='9555555555', status='won')
        changelist = reverse('admin:core_lead_changelist')
        self.client.post(changelist, {'action': 'mark_spam', '_selected_action': [spam.pk, won.pk]})
        self.client.post(changelist, {'action': 'mark_invalid', '_selected_action': [invalid.pk]})
        self.assertEqual(Lead.objects.get(pk=spam.pk).status, 'spam')
        self.assertEqual(Lead.objects.get(pk=invalid.pk).status, 'invalid')
        self.assertEqual(Lead.objects.get(pk=won.pk).status, 'won')

    def test_founder_can_record_a_whatsapp_lead_with_consent(self):
        response = self.client.post(reverse('admin:core_lead_add'), {
            'name': 'WhatsApp Person', 'phone': '90000 22222', 'service_type': 'cab',
            'travel_date_or_month': 'January', 'travellers': '3', 'status': 'new', 'lead_channel': 'whatsapp',
            'consent_given': 'on', 'consent_source': 'whatsapp_reply',
        })
        self.assertEqual(response.status_code, 302)
        lead = Lead.objects.get(name='WhatsApp Person')
        self.assertEqual(lead.lead_channel, 'whatsapp')
        self.assertEqual(lead.phone, '+919000022222')
        self.assertIsNotNone(lead.consent_at)
        self.assertEqual(lead.consent_notice_version, '2026-10-v1')

    def test_consent_without_source_is_rejected_in_admin(self):
        response = self.client.post(reverse('admin:core_lead_add'), {
            'name': 'X', 'phone': '9000022222', 'service_type': 'cab', 'travel_date_or_month': 'Jan',
            'travellers': '3', 'status': 'new', 'lead_channel': 'manual', 'consent_given': 'on',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)

    def test_channel_is_read_only_after_creation(self):
        lead = make_lead()
        response = self.client.get(reverse('admin:core_lead_change', args=[lead.pk]))
        self.assertNotIn('name="lead_channel"', response.content.decode())


class PartnerPilotColumnTests(TestCase):
    def test_admin_shows_referral_count_against_pilot_size(self):
        owner = get_user_model().objects.create_superuser('o2', 'o2@example.test', 'a-long-test-password-1')
        self.client.force_login(owner)
        partner = make_partner()
        for i in range(3):
            lead = make_lead(phone=f'91000000{i:02d}', consent_given=True, consent_source='manual')
            lead.partner = partner
            lead.save()
        spam = make_lead(phone='9100000099', status='spam')
        self.assertEqual(spam.partner, None)
        with override_settings(PILOT_REFERRALS_PER_PARTNER=3):
            response = self.client.get(reverse('admin:core_partner_changelist'))
        self.assertContains(response, '3 of 3 free - pilot used up')
        with override_settings(PILOT_REFERRALS_PER_PARTNER=5):
            response = self.client.get(reverse('admin:core_partner_changelist'))
        self.assertContains(response, '3 of 5 free')
