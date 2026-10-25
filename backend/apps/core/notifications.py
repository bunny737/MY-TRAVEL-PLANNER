import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)


def notify_new_lead(lead):
    """Email the founder a pointer to a new lead: the name and an admin link, never the phone or notes.

    Never raises: a mail outage must not lose or block the lead (it is already saved).
    """
    if not settings.LEAD_NOTIFY_EMAIL:
        return False
    link = settings.SITE_BASE_URL.rstrip('/') + reverse('admin:core_lead_change', args=[lead.pk])
    try:
        send_mail(
            subject=f'New {lead.get_service_type_display().lower()} enquiry',
            message=f'New enquiry from {lead.name}.\n\nOpen it in admin: {link}\n',
            from_email=None,
            recipient_list=[settings.LEAD_NOTIFY_EMAIL],
        )
    except Exception:
        logger.warning('Lead notification email failed for lead id %s', lead.pk)
        return False
    return True
