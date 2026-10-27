"""Blog articles (DRAFT). No prices anywhere: dated "from" amounts live on the package pages, and the articles link to them."""
from .common import ARTICLE, faq, notes, page

ARTICLES = [
    page(
        'what-changes-the-quote-for-an-araku-trip', 'araku-valley', ARTICLE,
        title='What Changes the Quote for an Araku Trip',
        meta_title='What Changes the Quote for an Araku Trip from Vizag',
        meta_description='Why two Araku quotes can differ: dates, vehicle, group size, stay type, season and extras. A plain guide to comparing quotes before you book.',
        intro='''
            Two quotes for the same Araku trip can differ a lot. This guide explains what moves the amount, so you can compare quotes
            fairly before you book.
        ''',
        hero_image='plantation', sort_order=10,
        body='''
            ## Start with the same trip
            Quotes are only comparable if they cover the same days, stops, pickup point and group. Write those down once and send the same details to everyone.

            ## What moves the quote
            Your date is the biggest factor: weekends, long weekends and festivals in the cooler months are busier than weekdays. After that come the vehicle and how many seats you need, the number of days, the stay type and whether meals are included.

            [photo: valley-road]

            ## What is often left out
            Check whether entry tickets, camera charges, local jeep rides (for example at Katiki Falls), boating or zipline, meals and the driver's food are in the amount. Ask about tolls, parking and any night charge too.

            ## Ask how the stay is charged
            Ask for the stay name, room type and whether the quote is for a twin room, one room or the whole group. Hotel category is the other big mover.

            ## Where to see sample amounts
            Where a partner has given us a recent quote, the package page shows a "from" amount with the date of that quote. It is a guide, not an offer: your own quote depends on your dates and group.

            ## Before you pay
            Get the quote in writing, with the inclusions and exclusions listed, and check the cancellation rules.
        ''',
        faq_text=faq(('Which is better, a package or building my own trip?',
                      'A package is simpler. Building your own gives you control over stops and stays. Ask for both and compare what each includes.')),
        internal_notes=notes('Replaces the partner "cost breakdown" article (which only divided its package prices). Add no amounts here: dated amounts belong in package price fields.', figures=False),
    ),
    page(
        'araku-in-two-days-from-vizag-sample-plan', 'araku-valley', ARTICLE,
        title='Araku in Two Days from Vizag: A Sample Plan',
        meta_title='Araku in Two Days from Vizag: A Sample 2D/1N Plan',
        meta_description='A relaxed two day, one night plan for Araku from Visakhapatnam: stop order, where to stay, what to carry and what to book early.',
        intro='''
            One night in Araku lets you enjoy the valley without racing the ghat road. Here is a sample plan, which you can reorder
            to suit your group.
        ''',
        hero_image='misty-pines', sort_order=20,
        body='''
            ## Day 1: up the ghat road
            Leave Visakhapatnam early and eat breakfast on the way. Stop at a viewpoint such as Dumuku, then reach Borra Caves in the morning, before the crowds. Katiki Falls is an optional short walk nearby if conditions are good.

            After lunch in Araku, the afternoon suits the Galikonda viewpoint, the Tribal Museum and Padmapuram Gardens. Check in, rest and keep the evening free for a stroll and coffee.

            [photo: plantation]

            ## Day 2: coffee, falls and the drive back
            Watch the morning mist if the weather allows, then visit the coffee museum or a plantation and Chaparai Falls. Aim to start back mid-afternoon so that most of the ghat road is in daylight.

            ## What to carry
            A light jacket, shoes with a good grip, water and snacks, a power bank, ID for hotel check-in and some cash.

            ## What to book early
            Train seats if you take the train, the stay (especially October to February and long weekends) and the vehicle.

            ## Want it arranged?
            Ask for a free quote for this plan and an independent local partner will quote it for your dates and group.
        ''',
        faq_text=faq(('Is this plan too packed?',
                      'It is a sample. Drop stops you do not care about. The ghat road already takes much of day 1.')),
        internal_notes=notes('Based on the partner sample 2D/1N day plan (times loosened). Their "best season" varies between pages: written as a range. VERIFY stop order with the partner.', figures=False),
    ),
    page(
        'best-time-to-visit-araku-and-lambasingi', 'araku-valley', ARTICLE,
        title='Best Time to Visit Araku and Lambasingi',
        meta_title='Best Time to Visit Araku and Lambasingi: Month Guide',
        meta_description='Which months suit Araku Valley and Lambasingi: cooler winter mornings, green monsoon hills and warmer summers, and what each season means for your plans.',
        intro='''
            There is no single best month, only the one that suits what you want to see. Here is how the seasons differ in Araku Valley
            and Lambasingi.
        ''',
        hero_image='lambasingi-clouds', sort_order=30,
        body='''
            ## October to February: cooler and clearer
            Most travellers pick these months. Days are comfortable for sightseeing, and Lambasingi's misty mornings are most likely. This is also the busiest time, so book the stay and vehicle early. Fog and frost cannot be promised for any given morning.

            ## March to June: warmer
            Warm days, so start early and keep the middle of the day for rest. The hills are cooler than the coast but not cold. Waterfalls run low.

            [photo: waterfall]

            ## July to September: monsoon
            The hills are very green and the waterfalls are fullest, but the ghat road and trails are wet and slippery. Plans can change with the weather, and some walks, such as the one to Katiki Falls, may be unsafe.

            ## Which should you choose?
            For mist and comfortable walking, choose the cooler months. For waterfalls and greenery, choose the monsoon or just after it. For fewer crowds and lower demand, ask about weekdays in the shoulder months.

            ## Planning tip
            Tell the partner what matters most, such as mist, waterfalls or a quiet trip, and ask what to expect on your dates.
        ''',
        faq_text=faq(('Is winter in Lambasingi very cold?',
                      'Mornings can be cold. Pack warm layers and ask whether your stay has enclosed rooms or heating.')),
        internal_notes=notes('Partner pages differ (October to February vs November to January): written as ranges. Temperatures and "coldest village" claims were not used.', figures=False),
    ),
    page(
        'araku-trip-from-hyderabad', 'araku-valley', ARTICLE,
        title='Planning an Araku Trip from Hyderabad',
        meta_title='Araku Trip from Hyderabad: Getting to Vizag and Beyond',
        meta_description='How travellers from Hyderabad reach Visakhapatnam by train, bus or flight, how many days to plan for Araku and Lambasingi, and what to book early.',
        intro='''
            Coming from Hyderabad? Here is how people reach Visakhapatnam, how many days to plan and what to book early.
        ''',
        hero_image='valley-dusk', sort_order=40,
        body='''
            ## Getting to Visakhapatnam
            A day train takes roughly 8.5 to 9 hours, overnight trains 11 to 13 hours, buses 11 to 14 hours and flights about an hour and ten minutes. Check current timetables and the airport your ticket uses, because services change.

            ## How many days
            Three days and two nights covers Visakhapatnam and Araku. Four days adds Lambasingi and gives the hills more time.

            [photo: rainbow-hills]

            ## A sample three days
            Day 1: arrive, check in and spend the evening at Kailasagiri or the beach. Day 2: drive up to Araku with stops at Borra Caves and a coffee plantation. Day 3: Chaparai Falls or a local stop, then return to Visakhapatnam for your journey home.

            ## Book early
            Trains fill up on Fridays, festivals and school holidays. Hotels and vehicles are in demand from October to February and on long weekends. If you take a night train, leave a buffer before your first day.

            ## Tips for out-of-town visitors
            Choose sleeper or comfortable seats for long journeys, check the drop point if you take a bus, and leave several hours before a return flight.
        ''',
        faq_text=faq(('Can the partner meet me at the station or airport?',
                      'Pickup from the station, airport or hotel is common. Share your arrival time in the enquiry.')),
        internal_notes=notes('Travel times come from one partner page: VERIFY before printing. The partner says flights moved to a new airport from 17 Aug 2026: VERIFY, then say so here. Fares left out (undated).', figures=True),
    ),
    page(
        'araku-by-train-or-by-cab', 'araku-valley', ARTICLE,
        title='Araku by Train or by Cab: How to Choose',
        meta_title='Araku by Train or Cab from Vizag: How to Choose',
        meta_description='Train or cab for the trip from Visakhapatnam to Araku? Compare time, comfort, flexibility and what each means for sightseeing stops.',
        intro='''
            Both the train and a private cab are good ways to reach Araku. Which suits you depends on how many stops you want and
            how you like to travel.
        ''',
        hero_image='valley-road', sort_order=50,
        body='''
            ## The cab
            A cab or car with a driver takes roughly 3.5 to 4.5 hours with stops and lets you stop at viewpoints, Borra Caves and Katiki Falls on the way. You control the pace and can travel with luggage easily.

            ## The train
            The passenger train on the Kirandul line takes about 4 to 5 hours and is popular for its views through tunnels and over bridges. It has no sightseeing stops of your own and you must reach the stations on time. Check the timetable and book early for weekends and holidays. Scenic-coach tickets are separate.

            ## Mixing the two
            A common choice is the train up and a cab back, or the cab up with stops and the train down. Ask your partner to quote the road part only.

            ## How to choose
            If you want the highlights on the way, choose the cab. If the journey itself is the point, choose the train. If you have young children, older relatives or lots of luggage, a cab is usually easier.
        ''',
        faq_text=faq(('Can I book only the cab for one direction?',
                      'Yes. Say which direction and the date, and the partner will quote that.')),
        internal_notes=notes('Train duration (4 to 5 h) and name come from partner pages with no timetable: VERIFY on IRCTC before publishing.', figures=True),
    ),
]
