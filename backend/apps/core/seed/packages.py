"""Tour package pages (DRAFT). One page per search intent; duration variants are itinerary blocks, not separate pages."""
from .common import (
    PACKAGE, STAY_INCLUDES, TRIP_EXCLUDES, TRIP_INCLUDES, faq, notes, page,
)

SUNRISE_TIP = 'Sunrise, mist and clouds depend on the weather on the day, so nobody can promise them.'

PACKAGES = [
    page(
        'vizag-to-araku-day-trip', 'araku-valley', PACKAGE,
        title='Vizag to Araku Day Trip',
        meta_title='Vizag to Araku Day Trip: Ask for Free Quotes',
        meta_description='Planning a one-day Araku trip from Visakhapatnam? Share your date and group size and an independent local partner sends you a quote. Free to ask.',
        intro='''
            Tell us your date and how many of you are travelling. An independent local partner sends you a quote
            for a one-day trip from Visakhapatnam to Araku Valley. Asking is free, and you book only if the quote suits you.
        ''',
        hero_image='valley-road', sort_order=10, duration='1 day', days=(1, 1),
        body='''
            Araku Valley is roughly 115 km from Visakhapatnam, and the ghat road up takes about 3.5 to 4.5 hours each way
            with stops. That makes a day trip a long day: an early start, a late return and a few well-chosen stops rather than every sight.

            Most day plans pick from the same list: viewpoints on the way up, Borra Caves, the coffee plantations, the Tribal
            Museum and one of the gardens or waterfalls. Tell your partner who is travelling and how much walking suits everyone,
            and they will shape the day around that.

            If you would like to see more without rushing, ask for the two-day version as well and compare the quotes.
        ''',
        itinerary='''
            Morning: the drive up (example)
            Leave Visakhapatnam very early and take the ghat road, with short stops at viewpoints such as Dumuku.
            Possible stops: Pets and Wings Araku Valley and Borra Caves, ideally before the crowds build.
            Katiki Falls is an optional short forest walk from the road; vehicles cannot reach the last stretch.

            Afternoon: around Araku (example)
            Lunch in or near Araku, then a coffee plantation, the Galikonda viewpoint and the Tribal Museum.

            Evening: the way back (example)
            Padmapuram Gardens or the coffee house if time allows, then the drive down. Ask your partner for a latest start
            on the return so the ghat road is not driven in the dark.
        ''',
        inclusions=TRIP_INCLUDES, exclusions=TRIP_EXCLUDES,
        faq_text=faq(
            ('Is one day enough for Araku?',
             'It is enough for the main highlights if you start early and pick your stops. For a slower trip, ask for a 2 day, 1 night plan.'),
            ('Can I take the train one way?',
             'Many travellers do. The partner can quote the road part separately. Check the current train timetable and book early for weekends and holidays.'),
            ('What should I wear?',
             'Comfortable shoes with a good grip for the caves and wet rocks, and a light jacket for the cooler hills.'),
            ('What changes the quote?',
             'Your date, the vehicle, the number of travellers and the stops you ask for. Weekends and holidays can differ from weekdays.'),
        ),
        internal_notes=notes('Stop list and order follow the partner day plan (10 stops); we show fewer on purpose. VERIFY: Katiki jeep and entry fees, Borra Caves hours.', figures=True),
    ),
    page(
        'araku-2-days-1-night-tour-package', 'araku-valley', PACKAGE,
        title='Araku 2 Days 1 Night Tour Package',
        meta_title='Araku 2 Days 1 Night Tour from Vizag: Free Quotes',
        meta_description='Two days and one night in Araku Valley from Visakhapatnam. Tell us your dates and group size and an independent local partner sends you a quote.',
        intro='''
            Tell us your dates and who is travelling. An independent local partner sends you a quote for two days and one night in
            Araku Valley, starting from Visakhapatnam. Asking is free, and there is no obligation to book.
        ''',
        hero_image='misty-pines', sort_order=20, duration='2 days / 1 night', days=(2, 2),
        body='''
            A night in Araku lets you see the sights on the way up on day one and spend the next morning in the valley without
            hurrying back down the ghat road. It suits couples, families and small groups.

            The plan below is an example. Your partner can change the order, drop stops you do not want and suggest a stay type
            that fits your group.
        ''',
        itinerary='''
            Day 1: Visakhapatnam to Araku (example)
            Pickup in Visakhapatnam and the drive up the ghat road with viewpoint stops such as Dumuku.
            Possible stops: Pets and Wings Araku Valley, Borra Caves and, if conditions allow, Katiki Falls.
            Afternoon at the Galikonda viewpoint, an Ananthagiri coffee plantation and the Tribal Museum, then check in at Araku.

            Day 2: Araku and back (example)
            Padmapuram Gardens, the coffee museum or chocolate-making stop, and the Pine Valley viewpoint.
            Chaparai Falls before the drive back, with a drop at the railway station or airport in Visakhapatnam.
        ''',
        inclusions=f'{TRIP_INCLUDES}\n{STAY_INCLUDES}', exclusions=TRIP_EXCLUDES,
        faq_text=faq(
            ('What kind of stay is included?',
             'The stay type depends on the quote. Ask the partner for the name, room type and what is included, and tell them your budget.'),
            ('Can I add Lambasingi?',
             'Yes. Ask for the Araku and Lambasingi plan, which adds a night in the hills and an early sunrise.'),
            ('Which time of year is best?',
             'Many travellers prefer October to February for cooler, clearer days. The monsoon months are greener but wetter and more slippery.'),
        ),
        internal_notes=notes('Order of stops follows the partner 2D/1N page; its Travel Guide section contradicts the itinerary (Vizag overnight) and was ignored. VERIFY hotel categories offered.', figures=False),
    ),
    page(
        'vizag-and-araku-3-days-tour-package', 'araku-valley', PACKAGE,
        title='Vizag and Araku 3 Days 2 Nights Tour Package',
        meta_title='Vizag and Araku 3 Days 2 Nights: Free Quotes',
        meta_description='See Visakhapatnam and Araku Valley in three days. Share your dates and group size and an independent local partner sends you a quote. Free to ask.',
        intro='''
            Tell us your dates and group size. An independent local partner sends you a quote for three days and two nights:
            a day in Visakhapatnam, then Araku Valley. Asking is free, and you book only if the quote suits you.
        ''',
        hero_image='kailasagiri-coast', sort_order=30, duration='3 days / 2 nights', days=(3, 3), also_visits=('vizag',),
        body='''
            This plan starts on the coast and finishes in the hills. It works well if you arrive by train or flight in
            Visakhapatnam and want a day for the beaches and city sights before the drive up.

            Your partner can reorder the days, for example Araku first and Vizag last, or trim the city day if you have seen it before.
        ''',
        itinerary='''
            Day 1: Visakhapatnam (example)
            Beaches and hilltop views: Rushikonda Beach, Kailasagiri and RK Beach in the evening.
            Possible stops: the Submarine and Aircraft museums, a temple visit and city viewpoints.

            Day 2: Visakhapatnam to Araku (example)
            Drive up the ghat road with stops such as Dumuku viewpoint, Borra Caves and Katiki Falls (a short forest walk, weather permitting).
            Afternoon at Galikonda viewpoint, a coffee plantation and the Tribal Museum, then check in at Araku.

            Day 3: Araku and back (example)
            An early start for a sunrise viewpoint such as Madagada if you wish, then breakfast and checkout.
            Chaparai Falls and Padmapuram Gardens before the drive down and the drop in Visakhapatnam.
        ''',
        inclusions=f'{TRIP_INCLUDES}\n{STAY_INCLUDES}', exclusions=TRIP_EXCLUDES,
        faq_text=faq(
            ('Where do we stay each night?',
             'Usually one night in Visakhapatnam and one in Araku. The partner names the stays in the quote.'),
            ('Can the order be reversed?',
             'Yes. Say so in your enquiry, for example if you land in Visakhapatnam late and want to go straight up to Araku.'),
            ('Will the sunrise viewpoint be clear?', SUNRISE_TIP),
        ),
        internal_notes=notes('Partner page repeats Padmapuram and the chocolate factory on days 2 and 3: listed once here. VERIFY: city day stops and timings.', figures=False),
    ),
    page(
        'araku-lambasingi-tour-package', 'lambasingi', PACKAGE,
        title='Araku and Lambasingi Tour Package',
        meta_title='Araku and Lambasingi Tour, 2 or 3 Days: Free Quotes',
        meta_description='Combine Araku Valley and Lambasingi in two or three days from Visakhapatnam. Share your dates and group size and a local partner sends you a quote.',
        intro='''
            Tell us your dates and group size. An independent local partner sends you a quote for Araku Valley and Lambasingi
            together, as a 2 day 1 night or a 3 day 2 night trip from Visakhapatnam. Asking is free.
        ''',
        hero_image='lambasingi-clouds', sort_order=40, duration='2 days / 1 night, or 3 days / 2 nights', days=(2, 3), also_visits=('araku-valley',),
        body='''
            Araku has the coffee plantations, caves and falls; Lambasingi is a quieter hill village known for misty
            mornings in the cooler months, a reservoir and seasonal strawberry patches. Doing both gives you sunrise in the hills.

            The two-day version is a long first day. The three-day version spends a night in Araku first and is more relaxed.
            Ask for both and compare.
        ''',
        itinerary='''
            2 days / 1 night, day 1: Araku route and up to Lambasingi (example)
            Pickup in Visakhapatnam, viewpoints, Borra Caves and a few Araku stops such as Galikonda, a plantation and Chaparai Falls.
            Kothapalli Falls on the way, then a night in Lambasingi.

            2 days / 1 night, day 2: Lambasingi and back (example)
            Sunrise at the village viewpoint, a strawberry plantation if it is in season, Thajangi Reservoir, then the drive back to Visakhapatnam.

            3 days / 2 nights, day 1: Visakhapatnam to Araku (example)
            Viewpoints, Borra Caves, Katiki Falls if conditions allow, a plantation and the Tribal Museum, then a night in Araku.

            3 days / 2 nights, day 2: Araku to Lambasingi (example)
            Padmapuram Gardens, the coffee museum or chocolate-making stop, Pine Valley viewpoint, Chaparai Falls and Kothapalli Falls, then check in at Lambasingi.

            3 days / 2 nights, day 3: Lambasingi and back (example)
            Early viewpoint, strawberry plantation (seasonal), Thajangi Reservoir and the drive down to Visakhapatnam.
        ''',
        inclusions=f'{TRIP_INCLUDES}\n{STAY_INCLUDES}', exclusions=TRIP_EXCLUDES,
        faq_text=faq(
            ('When are the misty mornings?',
             'Mostly in the cooler months, roughly November to February. Fog and frost cannot be promised on any given day.'),
            ('Are there many places to stay in Lambasingi?',
             'Fewer than in Araku, and mostly simple. Ask early, especially for winter weekends.'),
            ('Is the strawberry season fixed?',
             'No. It depends on the year. Ask your partner what is in season on your dates.'),
        ),
        internal_notes=notes('Partner 2D/1N plan packs about nine stops into day 1: shortened here. VERIFY: strawberry months, hotel types in Lambasingi, 4D/3N variant.', figures=False),
    ),
    page(
        'vanjangi-sunrise-tour-package', 'vanjangi', PACKAGE,
        title='Vanjangi Sunrise Tour Package',
        meta_title='Vanjangi Sunrise Tour from Vizag: Free Quotes',
        meta_description='Plan a Vanjangi sunrise trip with Araku and Lambasingi from Visakhapatnam. Share your dates and group size and a local partner sends you a quote.',
        intro='''
            Tell us your dates and group size. An independent local partner sends you a quote for a Vanjangi sunrise trip, usually
            combined with Araku Valley and Lambasingi. Asking is free, and you book only if the quote suits you.
        ''',
        hero_image='vanjangi-hills', sort_order=50, duration='2 to 5 days', days=(2, 5),
        body='''
            Vanjangi is a hilltop viewpoint known for sunrise, when clouds can fill the valley below. It is early, cold and
            weather-dependent, so plan a night nearby and keep some slack in your schedule.

            Most travellers add Vanjangi to an Araku or Araku and Lambasingi trip. Your partner can also arrange the jeep ride
            that the last part of the road may need.
        ''',
        itinerary='''
            Day 1: Visakhapatnam to Araku (example)
            Viewpoints, Borra Caves, Katiki Falls if conditions allow, Galikonda, a plantation and a night in Araku.

            Day 2: around Araku (example)
            Madagada viewpoint, Tribal Museum, coffee museum, Padmapuram Gardens, Pine Valley viewpoint and Chaparai Falls.

            Day 3: Vanjangi sunrise (example)
            A pre-dawn start for the viewpoint, then a temple and Kothapalli Falls, with a night near Lambasingi.

            Day 4: Lambasingi and back (example)
            Sunrise viewpoint, Thajangi Reservoir, seasonal strawberry farms and the drive back to Visakhapatnam.
        ''',
        inclusions=f'{TRIP_INCLUDES}\n{STAY_INCLUDES}', exclusions=f'{TRIP_EXCLUDES}\nThe local jeep to the Vanjangi viewpoint, paid on the spot',
        faq_text=faq(
            ('Will I see the sea of clouds?',
             SUNRISE_TIP + ' Clear, cool mornings in the winter months give the best chance.'),
            ('How early do we leave?',
             'Well before dawn. Your partner will tell you the time for your date, and a night close to the viewpoint helps.'),
            ('Is there phone signal?',
             'It can be patchy on the hill roads. Download maps and keep your partner’s number handy.'),
        ),
        internal_notes=notes('Partner Vanjangi page has 1N/2D to 4N/5D variants and a jeep fee (Rs 200 per person, undated): VERIFY the fee. Distances for Vanjangi were left out.', figures=False),
    ),
    page(
        'maredumilli-tour-package', 'maredumilli', PACKAGE,
        title='Maredumilli Tour Package',
        meta_title='Maredumilli Tour Package from Rajahmundry: Free Quotes',
        meta_description='Forest waterfalls and a night among the trees at Maredumilli. Share your dates and group size and an independent local partner sends you a quote.',
        intro='''
            Tell us your dates, group size and where you will start. An independent local partner sends you a quote for a trip to
            Maredumilli, usually from Rajahmundry. Asking is free, and you book only if the quote suits you.
        ''',
        hero_image='maredumilli-falls', sort_order=60, duration='2 days / 1 night', days=(2, 2),
        body='''
            Maredumilli is a forest area in the Papikonda range, known for its waterfalls, bamboo and teak trails and a quiet
            stay in the trees. It is usually done as a two-day trip from Rajahmundry, and it can also be reached from Visakhapatnam,
            though the drive is much longer.

            Forest roads are narrow and stays are limited, so ask early. Rules about entry and stays can change, so your partner
            will tell you what applies on your dates.
        ''',
        itinerary='''
            Day 1: Rajahmundry to Maredumilli (example)
            Early pickup in Rajahmundry and the drive into the forest.
            Check in, then Pamuleru Vaagu Falls and a forest walk, with meals at the stay.

            Day 2: waterfalls and temple (example)
            Nandanavanam garden, coffee plantations and Jalatarangini Falls.
            A temple visit on the way, then the drive back to Rajahmundry.
        ''',
        inclusions=f'{TRIP_INCLUDES}\n{STAY_INCLUDES}',
        exclusions='Entry or forest-department charges unless your quote lists them\nMeals and snacks unless your quote lists them\nPersonal expenses and shopping',
        faq_text=faq(
            ('Can I start from Visakhapatnam?',
             'Yes, but it is a long drive each way. Tell us your start point and the partner will say whether a longer plan suits you better.'),
            ('When are the waterfalls fullest?',
             'Usually in and after the monsoon, when trails are also wetter and more slippery. Cooler months are easier for walking.'),
            ('Are meals included?',
             'It depends on the quote. Say what you eat, and ask the partner to list meals clearly.'),
        ),
        internal_notes=notes('Partner Maredumilli page copies several sections from Vizag/Araku pages and calls the meals vegetarian while listing chicken. VERIFY: meals, entry rules, who runs the stay, start from Vizag.', figures=False),
    ),
    page(
        'vizag-araku-lambasingi-4-5-days-tour-package', 'araku-valley', PACKAGE,
        title='Vizag, Araku and Lambasingi 4 to 5 Days Tour Package',
        meta_title='Vizag, Araku and Lambasingi 4 to 5 Days: Free Quotes',
        meta_description='Coast, valley and hill village in four or five days from Visakhapatnam. Share your dates and group size and a local partner sends you a quote.',
        intro='''
            Tell us your dates and group size. An independent local partner sends you a quote for a longer trip that takes in
            Visakhapatnam, Araku Valley and Lambasingi. Asking is free, and you book only if the quote suits you.
        ''',
        hero_image='rushikonda-beach', sort_order=70, duration='4 to 5 days', days=(4, 5), also_visits=('vizag', 'lambasingi'),
        body='''
            A longer trip gives each place its own time: a day on the coast, a night in Araku and a night in Lambasingi, with
            room for a slower morning. It suits families and anyone who does not want to rush the hill roads.

            Your partner can add Vanjangi for sunrise or stretch the stay in Araku. Tell us how many days you have and where you
            will start and end.
        ''',
        itinerary='''
            Day 1: Visakhapatnam (example)
            Arrive, settle in and spend the evening at the beach or Kailasagiri.

            Day 2: Visakhapatnam sightseeing (example)
            Rushikonda Beach, museums and city sights at an easy pace.

            Day 3: up to Araku (example)
            Viewpoints on the ghat road, Borra Caves, a plantation and the Tribal Museum, then a night in Araku.

            Day 4: Araku to Lambasingi (example)
            Gardens, falls and the Pine Valley viewpoint, then on to Lambasingi for the night.

            Day 5: Lambasingi and back (example)
            Sunrise viewpoint, Thajangi Reservoir and the drive down to Visakhapatnam.
        ''',
        inclusions=f'{TRIP_INCLUDES}\n{STAY_INCLUDES}', exclusions=TRIP_EXCLUDES,
        faq_text=faq(
            ('Can it be shortened to four days?',
             'Yes. Ask for a four day plan, for example by combining the two Visakhapatnam days.'),
            ('Do you plan the days around my train or flight?',
             'Share your arrival and departure times in the enquiry and the partner will build the plan around them.'),
        ),
        internal_notes=notes('Partner pages disagree on the 4, 5 and 6 day plans. This is one merged example. VERIFY with the partner which day plan they actually run.', figures=False),
    ),
    page(
        'araku-honeymoon-package', 'araku-valley', PACKAGE,
        title='Araku Honeymoon and Couple Package',
        meta_title='Araku Honeymoon and Couple Trip: Free Quotes',
        meta_description='A quiet couple or honeymoon trip to Araku Valley and Lambasingi from Visakhapatnam. Share your dates and a local partner sends you a quote.',
        intro='''
            Tell us your dates and what would make the trip special. An independent local partner sends you a quote for a couple
            or honeymoon trip to Araku Valley and, if you like, Lambasingi. Asking is free.
        ''',
        hero_image='terraced-hills', sort_order=80, duration='1 to 5 days', days=(1, 5),
        body='''
            Couples usually pick the same routes as everyone else, with a private car and a stay chosen for quiet and views.
            Extras such as a candle-light dinner, a photographer or a room upgrade are not automatic: ask for them in your enquiry
            and the partner will say whether they can arrange them and what they add.

            A night or two in the hills is the usual choice; Lambasingi adds a misty sunrise in the cooler months.
        ''',
        itinerary='''
            1 day: Araku day trip (example)
            A relaxed version of the day trip, with the plantations, a viewpoint and a quiet stop, and fewer stops than the standard plan.

            2 days / 1 night: Araku (example)
            Viewpoints and Borra Caves on day one, a quiet evening in the hills, and gardens or falls the next morning.

            3 to 5 days: Araku and Lambasingi (example)
            A night or two in Araku, a night in Lambasingi, and, if you have time, a day in Visakhapatnam at the start or end.
        ''',
        inclusions=f'{TRIP_INCLUDES}\n{STAY_INCLUDES}',
        exclusions=f'{TRIP_EXCLUDES}\nExtras such as a special dinner, photography or a room upgrade, unless your quote lists them',
        faq_text=faq(
            ('Can you arrange a special dinner or photographer?',
             'Ask in your enquiry. The partner will say whether they can and what it adds to the quote.'),
            ('Which season is best for couples?',
             'Cooler months, roughly October to February, are popular. Book early for long weekends and holidays.'),
        ),
        internal_notes=notes('Add-ons (candle-light dinner, photography, upgrades) are on request on the partner site, never automatic: kept as questions. VERIFY which add-ons they can really arrange.', figures=False),
    ),
    page(
        'araku-group-tour-package', 'araku-valley', PACKAGE,
        title='Araku Group Tour Package',
        meta_title='Araku Group Tour by Tempo Traveller or Bus: Quotes',
        meta_description='Trips to Araku and Lambasingi for groups of eight or more, by tempo traveller or bus. Tell us your dates and size and a local partner sends a quote.',
        intro='''
            Tell us your dates, group size and where you start. An independent local partner sends you a quote for a group trip
            to Araku Valley and Lambasingi by tempo traveller or bus. Asking is free.
        ''',
        hero_image='plantation', sort_order=90, duration='1 to 5 days', days=(1, 5),
        body='''
            Groups of eight or more usually travel by tempo traveller, and larger groups may need a bus. Seat counts differ
            between operators, so give your exact numbers early.

            A few things make group trips smoother: name one person as the contact, share the final headcount a couple of days
            before travel, collect ID and food needs in advance, and book early for October to February. Weekdays are usually calmer than weekends.
        ''',
        itinerary='''
            Day trip: Araku (example)
            A tempo traveller from Visakhapatnam, Borra Caves, a plantation stop and a viewpoint, with the group back the same night.

            2 days / 1 night: Araku (example)
            The day trip route plus a group stay in Araku and the gardens or falls the next morning.

            Longer: Araku and Lambasingi, or Vizag, Araku and Lambasingi (example)
            Extra nights in the hills, with Kailasagiri and the beaches in Visakhapatnam if you want them.
        ''',
        inclusions='A group vehicle with a driver\nParking and tolls as agreed in the quote\nA group stay on overnight plans, as named in the quote\nA coordinator contact during the trip',
        exclusions='Entry tickets, guide fees and camera charges unless your quote lists them\nMeals, group dining and team activities\nExtra kilometres beyond the agreed route\nPersonal expenses',
        faq_text=faq(
            ('How big a group can you handle?',
             'Tell us your numbers. Tempo travellers and larger vehicles exist, and the partner will say what fits your group.'),
            ('Can we split into two vehicles?',
             'Yes, if that suits you better. Mention it in your enquiry so the quote covers both.'),
        ),
        internal_notes=notes('Partner group page gives per-group prices with no group size basis: not used. Bus seat counts overlap on the partner pages. VERIFY vehicle types and seats.', figures=False),
    ),
]
