from django.core.management.base import BaseCommand

from apps.core.models import ContentPage, Destination
from apps.core.seed.articles import ARTICLES
from apps.core.seed.guides import ATTRACTION_GUIDES, DESTINATION_GUIDES
from apps.core.seed.packages import PACKAGES
from apps.core.seed.transport import CABS, STAYS

# Vanjangi and Maredumilli are new destinations; Araku Valley, Lambasingi and Vizag come from seed_launch_content.
NEW_DESTINATIONS = [
    {'slug': 'vanjangi', 'name': 'Vanjangi', 'sort_order': 40, 'hero_image': 'vanjangi-hills',
     'summary': 'A hilltop sunrise viewpoint in the Eastern Ghats where clouds can fill the valley below. '
                'Usually combined with Araku Valley and Lambasingi.'},
    {'slug': 'maredumilli', 'name': 'Maredumilli', 'sort_order': 50, 'hero_image': 'maredumilli-falls',
     'summary': 'A forest area in the Papikonda range with waterfalls, bamboo and teak trails and a few forest stays, '
                'usually reached from Rajahmundry.'},
]
FALLBACK_DESTINATIONS = [
    {'slug': 'araku-valley', 'name': 'Araku Valley', 'sort_order': 10, 'hero_image': 'rainbow-hills', 'summary': ''},
    {'slug': 'lambasingi', 'name': 'Lambasingi', 'sort_order': 20, 'hero_image': 'lambasingi-valley', 'summary': ''},
    {'slug': 'vizag', 'name': 'Vizag', 'sort_order': 30, 'hero_image': 'kailasagiri-coast', 'summary': ''},
]

ALL_PAGES = PACKAGES + CABS + STAYS + DESTINATION_GUIDES + ATTRACTION_GUIDES + ARTICLES


class Command(BaseCommand):
    help = (
        'Create the DRAFT launch pages (packages, cabs, stays, guides, blog articles) and the Vanjangi and Maredumilli destinations, '
        'written from docs/research/partner-facts-2026-10.md. Never publishes, never sets a price, never overwrites an existing page. '
        'Safe to run again.'
    )

    def handle(self, *args, **options):
        destinations = {}
        for data in FALLBACK_DESTINATIONS + NEW_DESTINATIONS:
            fields = {key: value for key, value in data.items() if key != 'slug'}
            destination, created = Destination.objects.get_or_create(slug=data['slug'], defaults=fields)
            destinations[data['slug']] = destination
            if created and data in NEW_DESTINATIONS:
                self.stdout.write(self.style.SUCCESS(f'Created destination "{destination.name}".'))

        made = existing = 0
        for item in ALL_PAGES:
            page, created = ContentPage.objects.get_or_create(
                slug=item['slug'],
                defaults={**item['fields'], 'destination': destinations[item['destination']],
                          'status': ContentPage.Status.DRAFT},
            )
            if created:
                made += 1
                page.also_visits.set([destinations[slug] for slug in item['also_visits']])
            else:
                existing += 1
                self.stdout.write(f'Page "{item["slug"]}" already exists; left unchanged.')
        self.stdout.write(self.style.SUCCESS(
            f'Created {made} draft page(s); {existing} already existed. Review each in admin (Content pages), '
            'add the partner\'s dated price only if they gave one, then publish.'
        ))
