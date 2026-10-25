"""Destination and attraction guides (DRAFT). No prices, entry fees or opening hours: the partner site gives none we can date,
so each guide tells the visitor to confirm them. Body uses "## Heading" and "[photo: key]" lines."""
from .common import GUIDE, faq, notes, page

CONFIRM = 'Entry fees, opening times and what is open change, so confirm them when you book.'

DESTINATION_GUIDES = [
    page(
        'araku-valley-travel-guide', 'araku-valley', GUIDE,
        title='Araku Valley Travel Guide',
        meta_title='Araku Valley Travel Guide: Places, Season, Planning',
        meta_description='A plain guide to Araku Valley: the main places, the best season, how to get there from Visakhapatnam and how long to stay. Then ask for a free quote.',
        intro='''
            A short guide to planning a trip to Araku Valley: what to see, when to go, how to get there and how many days to allow.
            When you are ready, ask for a free quote and an independent local partner will plan it for your group.
        ''',
        hero_image='valley-dusk', sort_order=10,
        body='''
            ## What Araku Valley is
            Araku Valley is a hill region in the Eastern Ghats, in Andhra Pradesh, reached by road or train from Visakhapatnam. People go for the cooler air, coffee plantations, viewpoints, caves and waterfalls, and for the tribal culture of the area.

            ## The main places
            Borra Caves, the Tribal Museum, the coffee museum and plantations, Padmapuram Gardens, Chaparai Falls, the Galikonda and Pine Valley viewpoints and, for the adventurous, a short walk to Katiki Falls. Each has its own guide on this site.

            [photo: plantation]

            ## Getting there
            Araku is roughly 115 km from Visakhapatnam. By road it takes about 3.5 to 4.5 hours with stops. There is also a passenger train on the Kirandul line, which many travellers like for the views; check the current timetable and book early for weekends.

            ## Best time to go
            Many travellers prefer October to February for cooler, clearer days. The monsoon months, roughly July to September, are green and the falls are fuller, but trails are wet and slippery. March to June is warmer.

            ## How many days
            A day trip covers the highlights if you start very early. One night in Araku lets you see more without hurrying down the ghat road. Add Lambasingi for a misty sunrise in the cooler months.

            ## Good to know
            Carry some cash, a light jacket and grippy shoes. Network can be patchy on the ghat road. Drive up in daylight and start the return early.
        ''',
        faq_text=faq(
            ('Is Araku suitable for children and older family members?',
             'Most stops are easy, but Borra Caves has steps and damp floors, and Katiki Falls needs a walk. Tell the partner who is travelling and they will shape the plan.'),
        ),
        internal_notes=notes('Figures (115 km, 3.5 to 4.5 h) appear on many partner pages. Do not add fees or hours without a dated source.', figures=True),
    ),
    page(
        'lambasingi-travel-guide', 'lambasingi', GUIDE,
        title='Lambasingi Travel Guide',
        meta_title='Lambasingi Travel Guide: Mist, Season and Planning',
        meta_description='What to expect in Lambasingi: misty mornings, the viewpoint, Thajangi Reservoir and seasonal strawberries. Plan your trip, then ask for a free quote.',
        intro='''
            A short guide to Lambasingi, a small hill village that travellers combine with Araku Valley. Read what to expect, then ask
            for a free quote and an independent local partner will plan it.
        ''',
        hero_image='lambasingi-clouds', sort_order=20,
        body='''
            ## What Lambasingi is
            A quiet hill village in the Eastern Ghats, known for cool, misty mornings in the winter months, coffee and pepper estates and farms that grow strawberries and apples in season.

            ## What to see
            The village viewpoint at sunrise, Thajangi Reservoir, the plantations and farms on the slopes and Kothapalli Falls, which is fullest in and after the monsoon.

            [photo: lambasingi-valley]

            ## Mist and frost
            Fog and the occasional frost are the draw in the cooler months, but nobody can promise them for a given morning. Reach the viewpoint before sunrise and dress warmly.

            ## Getting there and staying
            There is no direct train, so most visitors come by private vehicle from Visakhapatnam or Araku. Stays are fewer and simpler than in Araku and fill up on winter weekends. Village shops are limited, so carry snacks and fuel.

            ## Best time to go
            November to February for the mist; the monsoon and after for green hills and waterfalls. Seasonal farms depend on the year.
        ''',
        faq_text=faq(
            ('Can I visit Lambasingi as a day trip?',
             'It is possible but very long. Most travellers stay a night nearby so they can catch the sunrise.'),
        ),
        internal_notes=notes('Partner claims "coldest village" and "close to 0 degrees" were not used (unsourced). VERIFY strawberry months and stay types.', figures=False),
    ),
    page(
        'vanjangi-sunrise-guide', 'vanjangi', GUIDE,
        title='Vanjangi Sunrise Viewpoint Guide',
        meta_title='Vanjangi Sunrise Viewpoint: What to Know Before You Go',
        meta_description='A guide to the Vanjangi sunrise viewpoint: when clouds fill the valley, how early to start and what to carry. Then ask for a free quote.',
        intro='''
            Vanjangi is a hilltop viewpoint known for sunrise over a valley that can fill with cloud. Here is what to know before you
            go; then ask for a free quote and a local partner will plan the early start.
        ''',
        hero_image='vanjangi-sunrise', sort_order=10,
        body='''
            ## What to expect
            A pre-dawn trip to a viewpoint where, on a good morning, clouds sit below the ridges. It is weather-dependent: clear skies and still air give the best chance, and nobody can promise it.

            ## When to go
            The cooler months, roughly October to March, are the usual choice.

            ## Getting there
            Travellers usually stay the night nearby in Araku or on the way to Lambasingi and set off in the dark. The last stretch may need a local jeep, which is paid on the spot.

            ## What to carry
            A warm layer, closed shoes, a torch or phone light, charged devices and cash. Phone signal can be patchy.

            ## Combine it with
            Araku Valley and Lambasingi, which are on the same side of the hills.
        ''',
        faq_text=faq(
            ('Is it worth the early start?',
             'Many travellers say yes on a clear morning, but it depends on the weather. Keep the rest of the day flexible.'),
        ),
        internal_notes=notes('Partner gives no sunrise time and unsourced distances for Vanjangi: none printed. VERIFY the jeep fee and the start point.', figures=False),
    ),
    page(
        'maredumilli-travel-guide', 'maredumilli', GUIDE,
        title='Maredumilli Travel Guide',
        meta_title='Maredumilli Travel Guide: Falls, Forest and Season',
        meta_description='A guide to Maredumilli: waterfalls, bamboo and teak forest, how to reach it from Rajahmundry and when to go. Then ask for a free quote.',
        intro='''
            Maredumilli is a forest area known for waterfalls and quiet trails. Read what to expect, then ask for a free quote and a
            local partner will plan your trip.
        ''',
        hero_image='maredumilli-forest', sort_order=10,
        body='''
            ## What Maredumilli is
            A forest region in the Papikonda range of the Eastern Ghats, in Alluri Sitharama Raju district, with waterfalls, bamboo and teak trails and a few forest stays.

            ## What to see
            Pamuleru Vaagu and Jalatarangini Falls, other seasonal cascades, the Nandanavanam garden and the forest drive. Treehouse and forest rest-house stays exist but are limited.

            ## Getting there
            Rajahmundry is the usual base; the drive takes roughly two hours or a little more. From Visakhapatnam it is a much longer day. Forest roads are narrow, so a driver who knows them helps.

            ## Best time to go
            October to February is comfortable for walking. In and after the monsoon the falls are fuller and the trails wetter. March to June is hot.

            ## Good to know
            Wear closed shoes, carry insect repellent and water, and expect patchy phone signal. Stays and trail access can change with forest rules, so confirm before you travel.
        ''',
        faq_text=faq(
            ('Do I need a permit?',
             'Entry rules can change. The partner will tell you what applies on your dates.'),
        ),
        internal_notes=notes('Partner states no permit or entry rules (VERIFY with the forest department). Figures (85 to 90 km, 2 to 2.5 h from Rajahmundry) come from one partner page.', figures=True),
    ),
    page(
        'things-to-do-in-vizag', 'vizag', GUIDE,
        title='Things to Do in Vizag',
        meta_title='Things to Do in Vizag: Beaches, Kailasagiri, Museums',
        meta_description='Beaches, Kailasagiri, museums and temples: a guide to what to do in Visakhapatnam and how it fits with a trip to Araku. Then ask for a free quote.',
        intro='''
            A short guide to Visakhapatnam, the coastal city where most Araku trips start. See what to do, then ask for a free quote
            and a local partner will plan it with your trip.
        ''',
        hero_image='kailasagiri-coast', sort_order=10,
        body='''
            ## On the coast
            RK Beach has a long promenade that is busy at sunset. Rushikonda Beach is a wider sandy beach outside the centre. Follow local safety advice near the water.

            [photo: rushikonda-beach]

            ## On the hill
            Kailasagiri is a hilltop park with views over the city and the Bay of Bengal, gardens, a large statue and a ropeway. Allow a few hours.

            ## Museums and temples
            The Submarine and Aircraft museums are close to the beach road, and there are several temples around the city. Opening times change, so confirm before you go.

            ## How long to stay
            One day covers the main beaches and Kailasagiri. Two days is more relaxed. Many travellers add a night in Visakhapatnam before or after Araku.

            ## Getting around
            A private car with a driver is the easiest way to link the beaches, the hill and the museums in a day. Airport and railway station pickups are common.
        ''',
        faq_text=faq(
            ('Can I combine Vizag with Araku?',
             'Yes. A three day plan often spends the first day in the city and the next two on the hills.'),
        ),
        internal_notes=notes('Partner Vizag page gives no hours or fees: none printed. Yarada Beach and named temples left out (no details). VERIFY museum days and times.', figures=False),
    ),
]

ATTRACTION_GUIDES = [
    page(
        'borra-caves-guide', 'araku-valley', GUIDE,
        title='Borra Caves Guide',
        meta_title='Borra Caves Guide: Visiting Tips and Timings',
        meta_description='What to expect at Borra Caves near Araku: the limestone formations, the walk inside, what to wear and how long to allow. Then ask for a free quote.',
        intro='''
            Borra Caves are limestone caves in the Ananthagiri hills, on the road up to Araku. Here is what to expect, what to wear and
            how long to allow. When you are ready, ask for a free quote.
        ''',
        hero_image='borra-caves', sort_order=30,
        body='''
            ## What you will see
            A cave system with stalactites and stalagmites, lit paths with steps and railings and a formation that many visitors say looks like a Shiva linga.

            ## How long to allow
            About 45 to 90 minutes inside, depending on the crowd and your pace.

            ## Tips
            Wear shoes with a good grip, since floors can be damp. Go in the morning if you can, and expect queues at weekends and holidays. There are no restrooms or drinking water inside, so use facilities before you enter. Keep food out of sight near the entrance, because monkeys are common. People with knee or mobility problems may want to go slowly or skip the deeper sections.

            ## Where it fits
            It is on the way from Visakhapatnam to Araku, near Katiki Falls and Pets and Wings Araku Valley, so most plans visit it on the way up. ''' + CONFIRM + '''
        ''',
        faq_text=faq(
            ('Is there a camera charge?',
             'Some places charge for cameras. Ask when you book.'),
        ),
        internal_notes=notes('Partner states hours "10 AM to 5 PM" and counters pausing at midday: not printed (VERIFY). Discovery date and age claims are unsourced: left out.', figures=False),
    ),
    page(
        'katiki-waterfalls-guide', 'araku-valley', GUIDE,
        title='Katiki Waterfalls Guide',
        meta_title='Katiki Waterfalls Guide: Walk, Season and Safety',
        meta_description='A guide to Katiki Falls near Borra Caves: the short forest walk, when the water is strongest and how to stay safe. Then ask for a free quote.',
        intro='''
            Katiki Falls is a waterfall reached by a short forest walk near Borra Caves. Read what to expect and when the water is
            strongest, then ask for a free quote.
        ''',
        hero_image='waterfall', sort_order=40,
        body='''
            ## What it is
            A waterfall of roughly 50 feet that drops into a natural pool, in forest near Borra Caves.

            ## Getting there
            Vehicles cannot reach the last stretch. You walk a few hundred metres through forest and small streams over rocky, sometimes wet paths. A local jeep ride and a small fee may apply; ask your partner what is current.

            ## When to go
            The flow is strongest from about July to December. January and February are cooler with gentler flow, and March to June is the driest. Mornings are better for light and for the walk.

            ## Safety
            Do not go during or just after heavy rain. A local guide is advisable. Wear shoes with a good grip and keep your phone in a waterproof pouch.

            ## Where it fits
            It is usually an optional stop on the way up to Araku, near Borra Caves. ''' + CONFIRM + '''
        ''',
        internal_notes=notes('Partner page lists no fee or time needed: not printed. Its sample itinerary reaches Katiki at 12:30 although it says morning is best: not copied. VERIFY jeep fee.', figures=False),
    ),
    page(
        'chaparai-waterfalls-guide', 'araku-valley', GUIDE,
        title='Chaparai Waterfalls Guide',
        meta_title='Chaparai Waterfalls Guide: Season, Safety and Tips',
        meta_description='A guide to Chaparai Falls near Araku: a wide cascade over flat rock, the best months, safety around slippery edges and what to carry.',
        intro='''
            Chaparai Falls is a wide, shallow cascade over flat rock near Araku town. Read when it is fullest and how to stay safe, then
            ask for a free quote.
        ''',
        hero_image='rainbow-hills', sort_order=50,
        body='''
            ## What it is
            Water flows over a broad rock bed through green hills, which makes it a popular picnic and photo stop.

            ## When to go
            Flow is strongest after the monsoon, roughly July to November. December to February is cooler with gentler flow, and March to June is reduced.

            ## Safety
            The water is shallow over most of the rock, but edges are slippery. Keep children close and avoid the deeper, steeper sections.

            ## What to carry
            Shoes with a good grip, a change of clothes, snacks and water, since shops nearby are limited.

            ## Where it fits
            It is close to Araku town and works well with the Tribal Museum and Padmapuram Gardens. ''' + CONFIRM + '''
        ''',
        internal_notes=notes('Partner calls it "safe for families" with no source: replaced with plain safety advice. No fee or visit time given: none printed.', figures=False),
    ),
    page(
        'padmapuram-gardens-guide', 'araku-valley', GUIDE,
        title='Padmapuram Gardens Guide',
        meta_title='Padmapuram Gardens Guide: What to See and When to Go',
        meta_description='A guide to Padmapuram Gardens in Araku: tree-top huts, the toy train and lawns, how long to spend and when to go. Then ask for a free quote.',
        intro='''
            Padmapuram Gardens is a botanical garden near Araku town with tree-top huts and a toy train. See what it offers and how
            long to allow, then ask for a free quote.
        ''',
        hero_image='valley-dusk', sort_order=60,
        body='''
            ## What it is
            A landscaped botanical garden near the town centre with flower beds, lawns, walking paths, bonsai and vegetable sections, a toy train and tree-top huts.

            ## How long to allow
            About 45 to 60 minutes is common.

            ## Tips
            The entry ticket is small, while the toy train and any hut stay are extra. Carry some cash, since card payment can be limited. Mornings are fresher and quieter.

            ## Where it fits
            A relaxed stop for families and older travellers, close to the Tribal Museum, the coffee museum and the Pinery. ''' + CONFIRM + '''
        ''',
        internal_notes=notes('Hut booking details are unclear on the partner page: no promise made. VERIFY entry fee and hut availability.', figures=False),
    ),
    page(
        'araku-coffee-museum-and-plantations', 'araku-valley', GUIDE,
        title='Araku Coffee Museum and Plantations',
        meta_title='Araku Coffee Museum and Plantation Visit: A Guide',
        meta_description='A guide to the coffee museum, coffee house and plantation walks in Araku: what you can see and taste and how long to allow. Then ask for a free quote.',
        intro='''
            Coffee is part of the Araku story. Here is what to expect at the coffee museum, the coffee house and the plantations, then
            ask for a free quote.
        ''',
        hero_image='plantation', sort_order=70,
        body='''
            ## The museum and coffee house
            The museum explains how coffee is grown, picked, dried, roasted and processed. There is a café with filter coffee and a shop selling beans and powder.

            ## Plantation walks
            The hills around Araku have shade-grown coffee with pepper vines climbing the trees. Many plans include a short walk through a plantation near Ananthagiri.

            ## How long to allow
            About 45 to 60 minutes for the museum. Plantation stops are usually shorter.

            ## Tips
            Morning is quieter. Carry cash for tasting and shopping, and buy sealed packs from shops you trust.

            ## Where it fits
            Usually combined with Padmapuram Gardens and the Tribal Museum. ''' + CONFIRM + '''
        ''',
        internal_notes=notes('Partner says entry is a state-tourism ticket without saying who runs the museum: operator not named here. "Award-winning" and "organic" claims left out (unsourced).', figures=False),
    ),
    page(
        'araku-tribal-museum-guide', 'araku-valley', GUIDE,
        title='Araku Tribal Museum Guide',
        meta_title='Araku Tribal Museum Guide: Exhibits and Visiting Tips',
        meta_description='A guide to the Tribal Museum in Araku: exhibits on tribal life, crafts to buy and Dhimsa dance shows on some days. Then ask for a free quote.',
        intro='''
            The Tribal Museum in Araku town shows how local tribal communities live and work. See what is on display and how to
            plan your visit, then ask for a free quote.
        ''',
        hero_image='misty-pines', sort_order=80,
        body='''
            ## What you will see
            Displays on tribal life including farming, cooking and festivals, along with tools, paintings, household items and jewellery. A shop sells handicrafts.

            ## Dhimsa dance
            A live Dhimsa dance is staged on some days at set times. Ask for the timings if you want to see it.

            ## How long to allow
            About 45 to 60 minutes at a relaxed pace.

            ## Tips
            Carry cash for crafts and any camera ticket. It works well as a mid-day indoor stop between outdoor sights, and on rainy days.

            ## Where it fits
            In Araku town, close to Padmapuram Gardens, the Pinery and Chaparai Falls. ''' + CONFIRM + '''
        ''',
        internal_notes=notes('Partner gives no hours, closed days, dance times or fees: none printed. VERIFY closed days.', figures=False),
    ),
    page(
        'araku-viewpoints-guide', 'araku-valley', GUIDE,
        title='Viewpoints Around Araku',
        meta_title='Araku Viewpoints: Dumuku, Galikonda, Madagada, Pinery',
        meta_description='A guide to the main viewpoints around Araku: Dumuku, Galikonda, Madagada and the Pine Valley viewpoint, and when each is at its best.',
        intro='''
            Several viewpoints dot the road to and around Araku. Here is what each is known for and when to go, then ask for a free quote.
        ''',
        hero_image='galikonda-view', sort_order=90,
        body='''
            ## Dumuku
            A roadside viewpoint on the way up from Visakhapatnam, a good first photo stop. Some pages spell it Damuku.

            ## Galikonda
            Wide views across the Eastern Ghats, best when the air is cool and clear. Fog can roll in fast, so carry a light jacket.

            ## Madagada
            Used for sunrise. Plans that include it start before dawn. ''' + 'Clouds and colour depend on the weather.' + '''

            ## Pine Valley and the Pinery
            Tall pine trees in a quiet forest area near Araku, pleasant for a short walk.

            ## Tips
            Start early, because light is softest in the morning. Phone signal can be weak in the hills.
        ''',
        internal_notes=notes('Partner calls the Pine Valley viewpoint and the Pinery by both names; kept together. No distances or timings given.', figures=False),
    ),
    page(
        'kailasagiri-guide', 'vizag', GUIDE,
        title='Kailasagiri Hill Park Guide',
        meta_title='Kailasagiri Guide: Views, Gardens and Ropeway in Vizag',
        meta_description='A guide to Kailasagiri in Visakhapatnam: the hilltop views, gardens, statue and ropeway, how long to spend and the best time of day.',
        intro='''
            Kailasagiri is a hilltop park inside Visakhapatnam with views of the city and the Bay of Bengal. See what is there and
            when to go, then ask for a free quote.
        ''',
        hero_image='kailasagiri-coast', sort_order=20,
        body='''
            ## What is there
            Landscaped gardens and paths, viewpoints over the city and the coast, a large Shiva-Parvati statue and an optional ropeway up the hill.

            ## How long to allow
            Two to three hours is common, including the viewpoints and the ropeway.

            ## When to go
            Early morning or late afternoon for clearer views and softer light. October to March is the comfortable season. Showers in the monsoon can reduce visibility.

            ## Tips
            Arrive early, bring water and a light jacket, and check ropeway timings on busy weekends. ''' + CONFIRM + '''
        ''',
        internal_notes=notes('No fees or hours on the partner page: none printed.', figures=False),
    ),
    page(
        'rk-beach-guide', 'vizag', GUIDE,
        title='RK Beach Guide',
        meta_title='RK Beach Guide: Sunset, Promenade and Nearby Museums',
        meta_description='A guide to RK Beach in Visakhapatnam: the promenade, the best time for sunset, nearby museums and sensible safety near the water.',
        intro='''
            RK Beach is Visakhapatnam's best-known city beach, with a long promenade. See when to go and what is nearby, then ask
            for a free quote.
        ''',
        hero_image='rushikonda-beach', sort_order=30,
        body='''
            ## What it is
            A wide promenade along the seafront, popular for evening walks and sunsets, with cafes and hotels nearby.

            ## When to go
            Late afternoon until sunset. October to March is pleasant; April to June is warm and breezy; July to September can bring showers.

            ## What is nearby
            The Submarine and Aircraft museums are close by, and Kailasagiri pairs well in the same day.

            ## Safety
            Follow local safety advice near the waterline, keep valuables light on crowded evenings, and do not swim where it is not allowed.
        ''',
        internal_notes=notes('Partner says nothing about swimming safety or facilities, so only generic advice is given.', figures=False),
    ),
]
