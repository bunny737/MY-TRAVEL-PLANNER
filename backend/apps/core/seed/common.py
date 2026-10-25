"""Shared helpers for the launch content seeds (seed_site_content).

Every page here is a DRAFT written in our own words from docs/research/partner-facts-2026-10.md. Nothing in these
files states a price (prices come only from a page's dated price fields), a rating, a review or a partner name.
Figures such as distances appear only where several partner pages agree, and the page's internal_notes say so.
"""
from inspect import cleandoc

from apps.core.models import ContentPage

PACKAGE = ContentPage.PageType.PACKAGE
CAB = ContentPage.PageType.CAB
STAY = ContentPage.PageType.STAY
GUIDE = ContentPage.PageType.GUIDE
ARTICLE = ContentPage.PageType.ARTICLE

FACT_SHEET = 'docs/research/partner-facts-2026-10.md'

ROLE_Q = (
    'Are you the tour operator?\n'
    'No. We are a travel enquiry and referral platform. Independent local partners prepare the quotes and run the trips.'
)
FREE_Q = (
    'Is it free to ask for a quote?\n'
    'Yes. Sending an enquiry costs nothing and you do not have to book.'
)
WHO_Q = (
    'Who will contact me?\n'
    'With your permission, we pass your enquiry to one suitable local partner, who contacts you with a quote.'
)


def text(value):
    """Dedent a triple-quoted block so the admin shows clean text."""
    return cleandoc(value)


def faq(*pairs, role=True):
    """FAQ field text from (question, answer) pairs, optionally starting with the standard referral-role answers."""
    blocks = [f'{q}\n{a}' for q, a in pairs]
    if role:
        blocks = [ROLE_Q, FREE_Q, WHO_Q] + blocks
    return '\n\n'.join(blocks)


def notes(*extra, figures=False):
    """Internal notes for the owner: where the facts came from and what to verify before publishing."""
    lines = [
        f'DRAFT written from the partner fact sheet ({FACT_SHEET}), in our own words. Before publishing:',
        '(1) get the partner\'s written OK and their dated quote; enter the price in the Price fieldset only if they gave one;',
        '(2) check each item flagged VERIFY in the fact sheet that touches this page;',
        '(3) read it once as a traveller and change anything you cannot stand behind.',
    ]
    if figures:
        lines.append('Figures on this page (distances, drive times, durations) come from the partner site, where several pages agree: confirm them.')
    lines.extend(extra)
    return ' '.join(lines)


def page(slug, destination, page_type, title, meta_title, meta_description, intro, hero_image, sort_order=100,
         duration='', body='', itinerary='', inclusions='', exclusions='', faq_text='', internal_notes=''):
    return {
        'slug': slug, 'destination': destination,
        'fields': {
            'page_type': page_type, 'title': title, 'meta_title': meta_title, 'meta_description': meta_description,
            'intro': text(intro), 'hero_image': hero_image, 'sort_order': sort_order, 'duration': duration,
            'body': text(body) if body else '', 'itinerary': text(itinerary) if itinerary else '',
            'inclusions': text(inclusions) if inclusions else '', 'exclusions': text(exclusions) if exclusions else '',
            'faq': faq_text, 'internal_notes': internal_notes,
        },
    }


# What a quote for a vehicle-based trip usually covers or leaves out (partner terms, to be confirmed in each quote).
TRIP_INCLUDES = '''
    Pickup and drop in Visakhapatnam (city, railway station or airport)
    A private vehicle with a driver for the whole route
    Driver allowance, parking and tolls
    Sightseeing stops as agreed in the plan
    Phone or WhatsApp coordination during the trip
'''

TRIP_EXCLUDES = '''
    Entry tickets for attractions, unless your quote lists them
    Camera charges at some places
    Local jeep rides, such as the one to Katiki Falls
    Boating, zipline and other optional activities
    Meals, snacks and the driver's food unless your quote says otherwise
    Personal expenses and shopping
'''

STAY_INCLUDES = 'A room for the night(s) in the stay type your quote names, usually twin or double sharing'
