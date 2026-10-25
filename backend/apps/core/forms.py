from django import forms

from .models import Lead
from .validators import normalize_phone


class EnquiryForm(forms.ModelForm):
    # Honeypot: hidden from people, filled by bots. Rendered in partials/enquiry_form.html.
    website = forms.CharField(required=False, max_length=200)
    notes = forms.CharField(
        required=False, max_length=1000, label='Anything else we should know? (optional)',
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. which places you would like to visit (Araku, Lambasingi, Vizag), stay or cab preferences'}),
    )

    class Meta:
        model = Lead
        fields = [
            'name', 'phone', 'service_type', 'travel_date_or_month', 'travellers',
            'pickup_city', 'budget', 'notes', 'consent_given',
        ]
        labels = {
            'name': 'Your name',
            'phone': 'Phone number',
            'service_type': 'What do you need?',
            'travel_date_or_month': 'Travel date or month',
            'travellers': 'Number of travellers',
            'pickup_city': 'Pickup / departure city (optional)',
            'budget': 'Budget (optional)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'inputmode': 'tel', 'autocomplete': 'tel'}),
            'travel_date_or_month': forms.TextInput(attrs={'placeholder': 'e.g. 15 Nov, or mid December'}),
            'travellers': forms.NumberInput(attrs={'min': 1, 'max': 100, 'inputmode': 'numeric'}),
            'budget': forms.TextInput(attrs={'placeholder': 'e.g. around 20,000'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Required (owner decision 2026-10-25): the service is passing the enquiry to a partner, so the form needs the
        # traveller's agreement to do that. Still unchecked by default: the visitor has to tick it themselves.
        self.fields['consent_given'].required = True
        self.fields['consent_given'].initial = False
        self.fields['consent_given'].error_messages['required'] = (
            'Please tick this box so we can pass your enquiry to a local partner for a quote.'
        )
        self.fields['service_type'].choices = [('', 'Choose one')] + list(Lead.ServiceType.choices)

    def clean_phone(self):
        return normalize_phone(self.cleaned_data['phone'])

    def clean(self):
        cleaned = super().clean()
        # Set before the model's own validation runs (it requires a source whenever consent is given).
        if cleaned.get('consent_given'):
            self.instance.consent_source = Lead.ConsentSource.FORM
        return cleaned
