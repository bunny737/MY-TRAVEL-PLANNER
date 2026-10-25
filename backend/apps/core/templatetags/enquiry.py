from django import template

from apps.core.forms import EnquiryForm

register = template.Library()


@register.inclusion_tag('partials/enquiry_form.html', takes_context=True)
def enquiry_form(context, form=None, service=''):
    """Drop the enquiry form into any page: {% load enquiry %}{% enquiry_form %}. It posts to /enquiry/.

    `service` ("tour" or "cab") pre-selects the service for pages about one thing.
    """
    if form is None:
        form = EnquiryForm(initial={'service_type': service} if service else None)
    return {
        'form': form,
        'csrf_token': context.get('csrf_token'),
        'site': context.get('site'),
    }
