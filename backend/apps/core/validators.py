import re

from django.core.exceptions import ValidationError

_INDIA_MOBILE = re.compile(r'^(?:\+?91|0)?([6-9]\d{9})$')
_INTERNATIONAL = re.compile(r'^\+\d{8,15}$')


def normalize_phone(raw):
    """Return the phone as '+91XXXXXXXXXX' (Indian mobile) or '+<digits>' (international), else raise.

    Spaces, dashes, dots and brackets are ignored. A bare 10-digit Indian mobile, or one prefixed with 91, +91 or 0,
    is accepted. Other countries must start with '+'.
    """
    cleaned = re.sub(r'[\s\-.()]', '', raw or '')
    match = _INDIA_MOBILE.match(cleaned)
    if match:
        return f'+91{match.group(1)}'
    if _INTERNATIONAL.match(cleaned):
        return cleaned
    raise ValidationError('Enter a valid phone number, for example 98765 43210 or +91 98765 43210.', code='invalid_phone')


def validate_phone(value):
    normalize_phone(value)
