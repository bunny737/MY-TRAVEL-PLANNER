"""Cab, tempo traveller and bus pages (DRAFT). The cab itinerary field holds vehicle, pickup and "what to ask" cards (see content_page.html)."""
from .common import CAB, STAY, faq, notes, page

STAY_NOTE = (
    'The property names and "from" rates in the Price options field come from the partner\'s hotel list and are applied by set_partner_prices '
    '(the partner site shows no date on them). We could NOT confirm the properties exist: the partner advertises more hotels than it lists, '
    'with stock photos. VERIFY every name with the partner before publishing and delete any line you cannot confirm. No ratings are shown.'
)

CABS = [
    page(
        'cab-service-in-vizag', 'vizag', CAB,
        title='Cab Service in Vizag',
        meta_title='Cab Service in Vizag: City, Airport and Outstation',
        meta_description='Need a cab in Visakhapatnam for the airport, a city tour or an outstation trip? Share your plan and independent local cab operators send you a quote.',
        intro='''
            Tell us where you are going, when and how many of you are travelling. Independent local cab operators send you a
            quote for city rides, airport transfers or outstation trips from Visakhapatnam. Asking is free.
        ''',
        hero_image='kailasagiri-coast', sort_order=20, duration='Hourly, day hire or outstation',
        body='''
            Cabs in Visakhapatnam are booked in three common ways: a transfer (for example airport to hotel), a block of
            hours for sightseeing in the city, or a day or longer for an outstation trip to Araku Valley, Lambasingi or beyond.

            The quote depends on the date, the vehicle, the hours or distance and whether you stay out overnight. Tell the partner
            if you have young children, older family members or a lot of luggage.
        ''',
        itinerary='''
            Cars for small groups (example)
            A hatchback or sedan usually suits couples and small families.
            Ask how many bags fit, especially for airport trips.

            SUVs for families (example)
            Often chosen by larger families and by groups with more luggage.
            Ask how many seats are really usable with the luggage you have.

            Tempo travellers (example)
            Usually chosen for big family groups, friends travelling together and office outings.
            Mention your group size early so the operator can check availability.

            Pickup points (example)
            Common choices are the airport, the railway station, the bus complex and your hotel.
            Give your exact pickup point and time in the enquiry.

            Questions to ask before you book (example)
            Is the quote for a transfer, a set number of hours or a full day, and what happens if you run over?
            Which tolls, parking and driver costs are included, and are there night charges?
            Which vehicle will come, and is the driver used to the route you want?
        ''',
        inclusions='A vehicle with a driver for the agreed route or hours\nPickup and drop at the places named in the quote\nTolls and parking, if the quote says so',
        exclusions='Attraction tickets\nMeals and personal expenses\nWaiting beyond the agreed time\nNight charges or permits for special routes, if the operator applies them',
        faq_text=faq(
            ('Can you arrange an airport pickup?',
             'Yes, ask for it in your enquiry and include your flight details so the pickup can be timed.'),
            ('Can I hire a cab for sightseeing in the city?',
             'Yes. Say how many hours or which places, and the operator will quote for that.'),
            ('Are there extra charges at night?',
             'Some operators apply them. Ask for the rule before you confirm.'),
        ),
        internal_notes=notes('Partner cab page quotes undated "from" rates for city, airport and Araku: ask for dated quotes and put them in the Price fieldset only then (unit: per vehicle per day or per trip, with the vehicle in "What the quote assumed"). VERIFY night charges and permit rules.', figures=False),
    ),
    page(
        'tempo-traveller-and-bus-hire-in-vizag', 'vizag', CAB,
        title='Tempo Traveller and Bus Hire in Vizag',
        meta_title='Tempo Traveller and Bus Hire in Vizag: Free Quotes',
        meta_description='Hire a tempo traveller, mini bus or bus in Visakhapatnam for groups, weddings and outings. Share your plan and a local operator sends you a quote.',
        intro='''
            Tell us your dates, group size and route. Independent local operators send you a quote for a tempo traveller, mini bus or
            bus from Visakhapatnam. Asking is free, and you book only if a quote suits you.
        ''',
        hero_image='valley-road', sort_order=30, duration='Hourly, day hire or multi-day',
        body='''
            Group vehicles are common for family trips, friends travelling together, school and office outings and wedding guests.
            Seat counts and vehicle types vary between operators, so give your exact numbers and the date.

            For corporate or event bookings, ask early and say how many pickup points you need. Quotes are normally given per trip or per
            day, with a limit on kilometres.
        ''',
        itinerary='''
            Tempo traveller (example)
            Usually 12 to 17 seats. Often used for friends and family groups and for day trips to Araku.

            Mini bus (example)
            Often chosen for medium groups, corporate outings, wedding guest transport and temple tours.

            Bus or coach (example)
            For larger groups, school and college trips and multi-day tours. Ask what comfort level and luggage space you get.

            Routes people ask for (example)
            A city sightseeing day in Visakhapatnam, Vizag to Araku for one to three days, Vizag to Lambasingi for one to two days,
            and event shuttles with several stops.

            Questions to ask before you book (example)
            How many seats does the vehicle have, and how many are usable with luggage?
            What kilometre limit applies, and what is charged beyond it?
            Are tolls, parking and driver costs in the quote?
        ''',
        inclusions='A vehicle with a driver for the agreed route\nRoute planning and basic coordination\nPickup and drop at the points named in the quote',
        exclusions='Tolls and parking unless your quote lists them\nPassenger meals and stays\nAttraction tickets\nKilometres beyond the agreed limit',
        faq_text=faq(
            ('How far ahead should I book?',
             'As early as you can, and earlier for weekends, holidays and October to February.'),
            ('Do you have buses for 40 or more people?',
             'Larger vehicles exist, and availability depends on the operator and date. Give your numbers and the partner will say what fits.'),
        ),
        internal_notes=notes('Partner bus page lists seat bands that overlap (35 to 50 and 40 to 49) and one undated per-km rate for tempo travellers: not printed. VERIFY real fleet and seat counts.', figures=True),
    ),
]

STAYS = [
    page(
        'araku-hotels-and-stays', 'araku-valley', STAY,
        title='Hotels and Stays in Araku Valley',
        meta_title='Hotels and Stays in Araku Valley: Ask for a Quote',
        meta_description='Looking for a place to stay in Araku Valley? Tell us your dates, group size and budget and an independent local partner sends you stay options and a quote.',
        intro='''
            Tell us your dates, how many rooms and people, and what kind of stay you like. An independent local partner sends you stay
            options and a quote. Asking is free, and you book only if a quote suits you.
        ''',
        hero_image='terraced-hills', sort_order=20, duration='Per night',
        body='''
            Araku has simple lodges and guest houses, mid-range hotels and resorts, a government-run family resort and nature camps
            with tents or cottages. Which one suits you depends on your budget, how much you want to be near the town, and the season.

            Winter weekends, long weekends and festivals fill up first. Ask early, and tell the partner if you need a family room,
            a quiet place, parking or help with a late arrival.

            The rates below are the "from" rates our partner shows for stays in Araku, per room per night. They are indicative: the
            room, the meals and availability depend on your dates. We show no ratings or reviews.
        ''',
        itinerary='''
            Budget lodges and guest houses (example)
            Simple rooms for short stays, often close to the town.
            Ask about hot water, parking and check-in times.

            Mid-range hotels and resorts (example)
            Usually more space and a restaurant on site.
            Ask whether meals are included and how far it is from the main sights.

            Camps and eco-stays (example)
            Tents or cottages in a natural setting, sometimes with a campfire.
            Ask about toilets, bedding and what the nights are like in the cooler months.
        ''',
        inclusions='A room for the dates in your quote, usually twin or double sharing\nThe room type and meals named in the quote',
        exclusions='Meals not listed in the quote\nExtra beds, early check-in or late checkout unless listed\nTransport, unless you ask for a package with a cab',
        faq_text=faq(
            ('Can I book only a stay without a tour?',
             'Yes. Choose "Hotel / stay" in the enquiry form and say your dates and the number of rooms.'),
            ('Can you bundle the stay with a cab and sightseeing?',
             'Yes, ask for a package. The partner will quote the stay and the cab together.'),
            ('When should I book?',
             'Early, especially for October to February, long weekends and festivals.'),
        ),
        internal_notes=notes(STAY_NOTE, figures=False),
    ),
    page(
        'lambasingi-hotels-and-stays', 'lambasingi', STAY,
        title='Hotels and Stays in Lambasingi',
        meta_title='Hotels and Stays in Lambasingi: Ask for a Quote',
        meta_description='Planning a night in Lambasingi? Tell us your dates, group size and budget and an independent local partner sends you stay options and a quote.',
        intro='''
            Tell us your dates, group size and what you want from the stay. An independent local partner sends you options and a quote
            for a night in Lambasingi. Asking is free.
        ''',
        hero_image='lambasingi-valley', sort_order=30, duration='Per night',
        body='''
            Lambasingi is a small village, so stays are fewer and simpler than in Araku. Expect resorts, cottages, a few budget inns
            and camps. In the cooler months, evenings are cold: ask about warm bedding, enclosed rooms and heating.

            Winter weekends fill quickly. Tell the partner your dates early and say whether you want to be close to the sunrise viewpoint.

            The rates below are the "from" rates our partner shows for stays in Lambasingi, per room per night. They are indicative: the
            room, the meals and availability depend on your dates. We show no ratings or reviews.
        ''',
        itinerary='''
            Resorts and cottages (example)
            Rooms or private cottages, sometimes with a campfire. Ask whether heating or extra blankets are provided.

            Budget inns (example)
            Basic rooms for short stays. Ask about food options, since village shops are limited.

            Camps and eco-stays (example)
            Tents or cottages in a natural setting. Ask about toilets, bedding and night temperatures.
        ''',
        inclusions='A room for the dates in your quote, usually twin or double sharing\nThe room type and meals named in the quote',
        exclusions='Meals not listed in the quote\nHeating or extra blankets unless the quote says so\nTransport, unless you ask for a package with a cab',
        faq_text=faq(
            ('Are there enough places to stay?',
             'There are fewer than in Araku, so ask early, especially for winter weekends.'),
            ('Should I carry food?',
             'Carry snacks and fuel. Village shops are limited.'),
        ),
        internal_notes=notes(STAY_NOTE, 'The partner Lambasingi page also gives two different winter temperature ranges: none printed.', figures=False),
    ),
    page(
        'vizag-hotels-and-stays', 'vizag', STAY,
        title='Hotels and Stays in Vizag',
        meta_title='Hotels and Stays in Vizag: Ask for a Quote',
        meta_description='Looking for a hotel in Visakhapatnam near the beach, the city or the station? Tell us your dates and budget and a local partner sends you a quote.',
        intro='''
            Tell us your dates, how many rooms and people, and where you want to be. An independent local partner sends you stay options
            and a quote for Visakhapatnam. Asking is free, and you book only if a quote suits you.
        ''',
        hero_image='rushikonda-beach', sort_order=40, duration='Per night',
        body='''
            Visakhapatnam has beach resorts along the coast road, city hotels in the main neighbourhoods, boutique and premium stays, budget hotels on the
            highway side and transit hotels by the railway station. Pick the area that matches your plan: the beach for sunsets, the city for
            business or shopping, the station for an early train.

            The rates below are the "from" rates our partner shows for stays in Visakhapatnam, per room per night. They are indicative: the
            room, the meals and availability depend on your dates. We show no ratings or reviews.
        ''',
        itinerary='''
            Beach and premium stays (example)
            Close to the sea, often with views. Ask about the walk to the beach, parking and breakfast.

            City and budget hotels (example)
            Handy for business trips and short stays. Ask about check-in times and distance from the station.

            Transit hotels near the station (example)
            Useful for an early train or a late arrival. Ask about short-stay options and luggage storage.
        ''',
        inclusions='A room for the dates in your quote, usually twin or double sharing\nThe room type and meals named in the quote',
        exclusions='Meals not listed in the quote\nExtra beds, early check-in or late checkout unless listed\nTransport, unless you ask for a package with a cab',
        faq_text=faq(
            ('Can you combine a hotel with an Araku trip?',
             'Yes. Ask for a package and the partner will quote the stay with the cab and sightseeing.'),
        ),
        internal_notes=notes(STAY_NOTE, figures=False),
    ),
    page(
        'maredumilli-hotels-and-stays', 'maredumilli', STAY,
        title='Hotels and Stays in Maredumilli',
        meta_title='Hotels and Stays in Maredumilli: Ask for a Quote',
        meta_description='Looking for a forest stay near Maredumilli? Tell us your dates and group size and an independent local partner sends you options and a quote.',
        intro='''
            Tell us your dates, group size and what you want from the stay. An independent local partner sends you options and a quote for a
            forest stay near Maredumilli. Asking is free.
        ''',
        hero_image='maredumilli-forest', sort_order=50, duration='Per night',
        body='''
            Stays near Maredumilli range from forest resorts and eco lodges to nature camps and village homestays. They are limited, and
            weekends and the cooler months fill up first, so ask early and say who is travelling.

            The rates below are the "from" rates our partner shows for stays near Maredumilli, per room per night. They are indicative: the
            room, the meals and availability depend on your dates. We show no ratings or reviews.
        ''',
        itinerary='''
            Resorts and eco lodges (example)
            Rooms or cottages in or near the forest. Ask about meals, since options nearby are few.

            Camps and homestays (example)
            Simple stays close to nature or village life. Ask about toilets, bedding and what the evenings are like.
        ''',
        inclusions='A room for the dates in your quote, usually twin or double sharing\nThe room type and meals named in the quote',
        exclusions='Meals not listed in the quote\nForest or entry charges unless listed\nTransport, unless you ask for a package with a cab',
        faq_text=faq(
            ('Do stays here need booking early?',
             'Yes, especially for weekends and the cooler months. Rules for forest stays can change, so ask what applies to your dates.'),
        ),
        internal_notes=notes(STAY_NOTE, figures=False),
    ),
]
