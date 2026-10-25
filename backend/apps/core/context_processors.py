from django.conf import settings


def _send_to(label):
    """'AW-ID/LABEL' for an Ads conversion, or '' unless both the Ads ID and that conversion's label are set."""
    return f'{settings.GOOGLE_ADS_ID}/{label}' if settings.GOOGLE_ADS_ID and label else ''


def site_config(request):
    """Business config reaches templates only through here (CLAUDE.md invariant 9)."""
    return {
        'site': {
            'name': settings.SITE_NAME,
            'base_url': settings.SITE_BASE_URL.rstrip('/'),
            'whatsapp_number': settings.WHATSAPP_NUMBER,
            'contact_email': settings.CONTACT_EMAIL,
            'contact_phone': settings.CONTACT_PHONE,
            'response_hours': settings.RESPONSE_HOURS_TEXT,
            'consent_notice_version': settings.CONSENT_NOTICE_VERSION,
        },
        'tracking': {
            'ga4_id': settings.GA4_MEASUREMENT_ID,
            'ads_id': settings.GOOGLE_ADS_ID,
            'ads_form_label': settings.GOOGLE_ADS_FORM_CONVERSION_LABEL,
            'ads_whatsapp_label': settings.GOOGLE_ADS_WHATSAPP_CONVERSION_LABEL,
            'ads_call_label': settings.GOOGLE_ADS_CALL_CONVERSION_LABEL,
            'ads_form_send_to': _send_to(settings.GOOGLE_ADS_FORM_CONVERSION_LABEL),
            'ads_whatsapp_send_to': _send_to(settings.GOOGLE_ADS_WHATSAPP_CONVERSION_LABEL),
            'ads_call_send_to': _send_to(settings.GOOGLE_ADS_CALL_CONVERSION_LABEL),
            'site_verification': settings.GOOGLE_SITE_VERIFICATION,
        },
    }
