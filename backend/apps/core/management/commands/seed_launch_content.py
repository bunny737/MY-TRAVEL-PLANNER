from django.core.management.base import BaseCommand

from apps.core.models import ContentPage, Destination

INTERNAL_NOTES = (
    'DRAFT written from general knowledge, not from field research. Before publishing: '
    '(1) check each stop, the order of stops and the drive time with the operators you call; '
    '(2) add the Inclusions and Exclusions the operators actually confirm (left empty on purpose); '
    '(3) keep the page free of prices; (4) read it once as a traveller and fix anything you cannot stand behind.'
)

ARAKU_PAGE = {
    'page_type': ContentPage.PageType.PACKAGE,
    'title': 'Araku Tour Packages from Vizag',
    'meta_title': 'Araku Tour Packages from Vizag: Request Free Quotes',
    'meta_description': (
        'Planning a trip to Araku Valley from Visakhapatnam? Tell us your dates and group size and '
        'independent local operators send you quotes. Free to ask.'
    ),
    'intro': (
        'Tell us when you want to travel and how many of you are going. Independent local tour operators '
        'send you quotes for Araku Valley trips from Visakhapatnam. Asking is free, and you only book if a '
        'quote suits you.'
    ),
    'hero_image': 'galikonda-view',
    'duration': 'Day trip, or 2 days / 1 night',
    'body': (
        'Araku Valley is a hill region in the Eastern Ghats, roughly 110 km from Visakhapatnam. Most visitors '
        'drive up through the winding ghat road, stopping at viewpoints on the way, and spend their time among '
        'coffee plantations, waterfalls, caves and tribal culture.\n\n'
        'Whether you want a long day out or a night in the hills, a local operator can plan the route, vehicle '
        'and stops around your group. Tell us what matters to you, such as travelling with children or older '
        'family members, and mention it in your enquiry.'
    ),
    'itinerary': (
        'Day trip from Visakhapatnam (example)\n'
        'Early start from Visakhapatnam and drive up the ghat road, with photo stops at viewpoints.\n'
        'Possible stops on the way: Borra Caves and Katiki Falls (the falls run best after the rains).\n'
        'Time in Araku for the coffee plantations and the tribal museum, then the drive back, usually reaching '
        'Visakhapatnam in the evening.\n\n'
        '2 days / 1 night, day 1: Visakhapatnam to Araku (example)\n'
        'Drive up the ghat road with viewpoint stops.\n'
        'Possible stops: Borra Caves, Katiki Falls and Tyda.\n'
        'Check in at Araku and spend the evening at leisure.\n\n'
        '2 days / 1 night, day 2: Araku and back (example)\n'
        'Coffee plantation visit and the tribal museum.\n'
        'Padmapuram Gardens, if time allows.\n'
        'Drive back to Visakhapatnam by evening.'
    ),
    'faq': (
        'Are you the tour operator?\n'
        'No. We are a travel enquiry and referral platform. Independent local operators prepare the quotes '
        'and run the trips.\n\n'
        'Is it free to ask for quotes?\n'
        'Yes. Sending an enquiry costs nothing and you do not have to book.\n\n'
        'Who will contact me?\n'
        'With your permission, we pass your enquiry to one suitable local operator, who contacts you with a quote.\n\n'
        'What does the quote depend on?\n'
        'Your travel dates, the number of travellers, the type of vehicle, whether you stay overnight and what '
        'you ask to include.\n\n'
        'When is a good time to visit?\n'
        'Many travellers prefer the cooler months, roughly October to February. Waterfalls and greenery look '
        'different through the year, so ask the operator what to expect on your dates.'
    ),
    'internal_notes': INTERNAL_NOTES,
}

# Lambasingi and Vizag drafts (owner request 2026-10-25). Same rules as the Araku page: no prices, no distances or
# temperatures we cannot source, stops written as "possible", and the notes tell the owner what to verify.
LAMBASINGI_PAGE = {
    'page_type': ContentPage.PageType.PACKAGE,
    'title': 'Lambasingi Tour Packages',
    'meta_title': 'Lambasingi Tour Packages from Vizag: Request Free Quotes',
    'meta_description': (
        'Planning a trip to Lambasingi from Visakhapatnam? Share your dates and group size and independent '
        'local operators send you quotes. Free to ask.'
    ),
    'intro': (
        'Tell us when you want to visit Lambasingi and how many of you are travelling. Independent local '
        'operators send you quotes, and you only book if one suits you.'
    ),
    'hero_image': 'lambasingi-clouds',
    'duration': 'Day trip, or 2 days / 1 night',
    'body': (
        'Lambasingi is a small village in the hills of the Eastern Ghats, reached by road from Visakhapatnam. '
        'Visitors come mainly for the cool, misty mornings of the winter months, the plantations on the slopes '
        'and the quiet countryside.\n\n'
        'Many travellers combine Lambasingi with Araku Valley or with a few days in Vizag. Tell us which places '
        'you would like to see and the operator can plan the route and vehicle around your group.'
    ),
    'itinerary': (
        'Day trip from Visakhapatnam (example)\n'
        'Very early start to reach the hills while the morning mist is still around.\n'
        'Possible stops: viewpoints near the village, plantations and the Thajangi reservoir.\n'
        'Drive back to Visakhapatnam in the evening.\n\n'
        '2 days / 1 night, day 1: Visakhapatnam to Lambasingi (example)\n'
        'Drive into the hills in the afternoon and stay overnight nearby.\n\n'
        '2 days / 1 night, day 2: Lambasingi and back (example)\n'
        'Sunrise at a viewpoint, then plantations or seasonal farms if they are open.\n'
        'Drive back to Visakhapatnam, or continue towards Araku Valley if you planned a longer trip.'
    ),
    'faq': (
        'Are you the tour operator?\n'
        'No. We are a travel enquiry and referral platform. Independent local operators prepare the quotes '
        'and run the trips.\n\n'
        'Is it free to ask for quotes?\n'
        'Yes. Sending an enquiry costs nothing and you do not have to book.\n\n'
        'When is a good time to visit?\n'
        'Most visitors go in the cooler months for the misty mornings. Ask the operator what to expect on your dates.\n\n'
        'Can I combine Lambasingi with Araku or Vizag?\n'
        'Yes. Tell us every place you want to visit in your enquiry and the operator can quote for the whole trip.'
    ),
    'internal_notes': INTERNAL_NOTES,
}

VIZAG_PAGE = {
    'page_type': ContentPage.PageType.PACKAGE,
    'title': 'Vizag Sightseeing Tours',
    'meta_title': 'Vizag Sightseeing Tours: Request Free Quotes',
    'meta_description': (
        'Sightseeing in Visakhapatnam: beaches, Kailasagiri and more. Share your dates and group size and '
        'independent local operators send you quotes. Free to ask.'
    ),
    'intro': (
        'Tell us your dates and how many of you are travelling. Independent local operators send you quotes for '
        'sightseeing in and around Visakhapatnam, and you only book if one suits you.'
    ),
    'hero_image': 'rushikonda-beach',
    'duration': 'Half day, full day or longer',
    'body': (
        'Visakhapatnam (Vizag) is a coastal city on the Bay of Bengal and the usual starting point for trips to '
        'Araku Valley and Lambasingi. Visitors spend time on its beaches, at the Kailasagiri hilltop park and at '
        'the museums and temples around the city.\n\n'
        'Tell us what you would like to see, how long you have and who is travelling, and a local operator can '
        'suggest a route and a vehicle for your group.'
    ),
    'itinerary': (
        'City sightseeing day (example)\n'
        'Morning at Kailasagiri hill for the views over the city and the coast.\n'
        'Possible stops: the submarine museum and other sights along the beach road.\n'
        'Evening at Ramakrishna (RK) Beach.\n\n'
        'Coast drive (example)\n'
        'Drive along the coast towards Rushikonda beach, with stops at viewpoints on the way.\n'
        'Possible stops: the Thotlakonda Buddhist site and other sights the operator suggests.'
    ),
    'faq': (
        'Are you the tour operator?\n'
        'No. We are a travel enquiry and referral platform. Independent local operators prepare the quotes '
        'and run the trips.\n\n'
        'Is it free to ask for quotes?\n'
        'Yes. Sending an enquiry costs nothing and you do not have to book.\n\n'
        'Can you also arrange a trip to Araku or Lambasingi?\n'
        'Yes. Mention them in your enquiry and the operator can quote for the whole trip.'
    ),
    'internal_notes': INTERNAL_NOTES,
}

# Module 08. The cab page reuses the itinerary field for "Vehicles, pickup points and what to ask" cards (the page template
# titles that section by page type), so each block below is one card. No prices, no seat counts or distances we cannot source.
CAB_NOTES = (
    'DRAFT written from general knowledge, not from field research. Before publishing: '
    '(1) ask your cab partners which vehicle types they really have and edit the vehicle cards to match; '
    '(2) check the pickup points; '
    '(3) add the Inclusions and Exclusions the operators actually confirm (left empty on purpose); '
    '(4) keep the page free of prices; '
    '(5) publishing the page is fine, but do NOT start any cab ads until at least one active cab partner has agreed to '
    'receive referrals (Partners > offers cabs > referral terms date) and confirmed they can serve this route.'
)

CAB_PAGE = {
    'page_type': ContentPage.PageType.CAB,
    'title': 'Vizag to Araku Cab',
    'meta_title': 'Vizag to Araku Cab: Request Free Quotes',
    'meta_description': (
        'Need a cab from Visakhapatnam to Araku Valley? Share your dates, group size and pickup point and '
        'independent local cab operators send you quotes. Free to ask.'
    ),
    'intro': (
        'Tell us when you travel, how many of you are going and where to pick you up. Independent local cab '
        'operators send you quotes for the drive from Visakhapatnam to Araku Valley. Asking is free, and you only '
        'book if a quote suits you.'
    ),
    'hero_image': 'valley-road',
    'duration': 'One way, round trip or day trip',
    'body': (
        'Most visitors reach Araku Valley by road from Visakhapatnam (Vizag), up the ghat road. You can ask for a '
        'one-way transfer, or for a cab and driver for the whole day or longer so you can stop at viewpoints, Borra '
        'Caves and other places on the way.\n\n'
        'The quote depends on your dates, the type of vehicle, the distance you cover and whether you stay '
        'overnight. Mention anything that matters, such as young children, older family members or a late return, '
        'in your enquiry.'
    ),
    'itinerary': (
        'Cars for small groups (example)\n'
        'A hatchback or sedan usually suits couples and small families.\n'
        'Seats and luggage space differ between vehicles, so tell the operator how many people and bags to expect.\n\n'
        'SUVs and larger cars for families (example)\n'
        'Often chosen by bigger families and by groups with more luggage.\n'
        'Ask the operator how many seats the vehicle really has and where the luggage goes.\n\n'
        'Tempo travellers and other large vehicles (example)\n'
        'Usually chosen for big family groups, friends travelling together and office outings.\n'
        'Availability and seat counts vary by operator, so mention your group size early.\n\n'
        'Pickup points in Visakhapatnam (example)\n'
        'Common choices are the airport, the railway station, the bus complex and your hotel.\n'
        'Give the operator your exact pickup point and time in your enquiry.\n\n'
        'Questions to ask before you book (example)\n'
        'Is the quote for one way or a round trip, and for how many hours of use?\n'
        'What happens if your plan changes on the day, such as a later return?\n'
        'Which tolls, parking and driver costs are included in the quote?\n'
        'Which vehicle will come, and is the driver used to the ghat road?'
    ),
    'faq': (
        'Are you the cab operator?\n'
        'No. We are a travel enquiry and referral platform. Independent local cab operators prepare the quotes '
        'and provide the cabs.\n\n'
        'Is it free to ask for quotes?\n'
        'Yes. Sending an enquiry costs nothing and you do not have to book.\n\n'
        'Can I ask for a one-way transfer?\n'
        'Tell us whether you need one way or a round trip, and the operator will quote for that.\n\n'
        'Can the cab also stop at Borra Caves or other places on the way?\n'
        'Mention the stops you want in your enquiry and the operator will say whether they fit your time.\n\n'
        'How far ahead should I ask?\n'
        'As early as you can. It gives the operator more time to find a suitable vehicle for your dates.'
    ),
    'internal_notes': CAB_NOTES,
}

DESTINATIONS = [
    {'slug': 'araku-valley', 'name': 'Araku Valley', 'sort_order': 10, 'hero_image': 'rainbow-hills',
     'summary': 'A hill valley in the Eastern Ghats: coffee plantations, viewpoints, and Borra Caves and waterfalls '
                'along the ghat road from Visakhapatnam.'},
    {'slug': 'lambasingi', 'name': 'Lambasingi', 'sort_order': 20, 'hero_image': 'lambasingi-valley',
     'summary': 'A small hill village known for misty winter mornings, plantations and quiet countryside. '
                'Often combined with Araku.'},
    {'slug': 'vizag', 'name': 'Vizag', 'sort_order': 30, 'hero_image': 'kailasagiri-coast',
     'summary': 'Visakhapatnam, the coastal city where most trips start: beaches, the Kailasagiri hilltop park and '
                'city sightseeing.'},
]

# (page slug, destination slug, page fields)
PAGES = [
    ('araku-tour-packages', 'araku-valley', ARAKU_PAGE),
    ('lambasingi-tour-packages', 'lambasingi', LAMBASINGI_PAGE),
    ('vizag-tour-packages', 'vizag', VIZAG_PAGE),
    ('vizag-to-araku-cab', 'araku-valley', CAB_PAGE),
]


class Command(BaseCommand):
    help = (
        'Create the launch destinations (Araku Valley, Lambasingi, Vizag), a DRAFT package page for each and the DRAFT '
        'Vizag to Araku cab page, to edit in admin. Never publishes anything and never overwrites a page that already exists.'
    )

    def handle(self, *args, **options):
        destinations = {}
        for data in DESTINATIONS:
            fields = {key: value for key, value in data.items() if key != 'slug'}
            destination, created = Destination.objects.get_or_create(slug=data['slug'], defaults=fields)
            if not created:
                # Fill only what the owner has left blank (or at the default order); never overwrite their edits.
                blank = [key for key in ('summary', 'hero_image') if not getattr(destination, key)]
                if destination.sort_order == Destination._meta.get_field('sort_order').default:
                    blank.append('sort_order')
                for key in blank:
                    setattr(destination, key, data[key])
                if blank:
                    destination.save(update_fields=blank)
            destinations[data['slug']] = destination

        for slug, destination_slug, fields in PAGES:
            page, created = ContentPage.objects.get_or_create(
                slug=slug,
                defaults={**fields, 'destination': destinations[destination_slug], 'status': ContentPage.Status.DRAFT},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created draft "{page.title}". Review it in admin, add confirmed inclusions, then publish.'
                ))
            else:
                self.stdout.write(f'Page "{slug}" already exists; left unchanged.')
