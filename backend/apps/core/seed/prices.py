"""Partner "from" prices for the launch pages, read from the partner's public site on 2026-10-25 (owner decision: show the same packages and
hotels with the same prices, with the partner's written OK). Applied by `set_partner_prices`, never by the content seed.

Each page gets its lowest option as the headline "from" amount and, when there are several options, a list of them (the Price options field).
Hotels are listed per property inside one stay page per destination, as the partner's own hotel pages do.

Dates: the partner site prints "Prices last updated: 24 October 2026" on some package pages only (`dated=True` below). Everything else is shown
with no date there; the owner chose to use it with the same date, and each page's internal notes say so.
Still not shown (no figures on the partner pages): cab fares per route, tempo traveller and bus rates.
"""
from decimal import Decimal

PER_COUPLE = 'per_couple'
PER_VEHICLE_TRIP = 'per_vehicle_trip'
PER_ROOM_NIGHT = 'per_room_night'

DEFAULT_QUOTED_ON = '2026-10-24'

COUPLE_BASIS = 'Per couple; the vehicle and the stay are named in your quote'
STAY_BASIS = 'Rate per room per night; the room type and availability depend on your dates'


def _options(*pairs):
    return [(label, Decimal(str(amount))) for label, amount in pairs]


# (page slug, unit, what the quote assumed (max 120 characters), date printed on the partner page?, [(option label, amount in INR)])
PRICES = [
    ('araku-tour-packages', PER_COUPLE, COUPLE_BASIS, False, _options(
        ('1 day', 6000), ('2 days / 1 night', 9000), ('3 days / 2 nights, with Vizag', 18000))),
    ('vizag-to-araku-day-trip', PER_COUPLE, 'Day trip from Visakhapatnam for a couple; the vehicle is named in your quote', True, _options(
        ('1 day', 6000))),
    ('araku-2-days-1-night-tour-package', PER_COUPLE, '2 days / 1 night from Visakhapatnam with a night in Araku, for a couple', False, _options(
        ('2 days / 1 night', 9000))),
    ('vizag-and-araku-3-days-tour-package', PER_COUPLE, '3 days / 2 nights, a night in Vizag and a night in Araku, for a couple', True, _options(
        ('3 days / 2 nights', 18000))),
    ('araku-lambasingi-tour-package', PER_COUPLE, COUPLE_BASIS, False, _options(
        ('2 days / 1 night', 15000), ('3 days / 2 nights', 22500), ('4 days / 3 nights', 26000))),
    ('lambasingi-tour-packages', PER_COUPLE, COUPLE_BASIS, False, _options(
        ('Araku and Lambasingi, 2 days / 1 night', 15000), ('Araku and Lambasingi, 3 days / 2 nights', 22500),
        ('Araku and Lambasingi, 4 days / 3 nights', 26000))),
    ('vanjangi-sunrise-tour-package', PER_COUPLE, COUPLE_BASIS, False, _options(
        ('2 days / 1 night, Araku and Vanjangi', 11999), ('3 days / 2 nights, Vizag, Araku and Vanjangi', 15999),
        ('4 days / 3 nights, with Lambasingi', 23999), ('5 days / 4 nights, with Vizag sightseeing', 31999))),
    ('maredumilli-tour-package', PER_COUPLE, '2 days / 1 night from Rajahmundry, for a couple', False, _options(
        ('2 days / 1 night', 18500))),
    ('vizag-tour-packages', PER_COUPLE, 'Vizag sightseeing for a couple; the vehicle and the stay are named in your quote', True, _options(
        ('1 day', 6000), ('2 days / 1 night', 9000), ('3 days / 2 nights', 14000))),
    ('vizag-araku-lambasingi-4-5-days-tour-package', PER_COUPLE, COUPLE_BASIS, False, _options(
        ('4 days / 3 nights', 27500), ('5 days / 4 nights', 34500))),
    ('araku-honeymoon-package', PER_COUPLE, COUPLE_BASIS, False, _options(
        ('1 day', 6000), ('2 days / 1 night, Araku', 9000), ('2 days / 1 night, Araku and Lambasingi', 15000),
        ('3 days / 2 nights, Araku and Lambasingi', 22500), ('4 days / 3 nights, Araku and Lambasingi', 26000),
        ('5 days / 4 nights, Vizag, Araku and Lambasingi', 34500))),
    ('araku-group-tour-package', PER_VEHICLE_TRIP, 'Group of 8 or more by tempo traveller; the final amount depends on group size', False, _options(
        ('1 day, Araku', 18000), ('2 days / 1 night, Araku', 32000), ('2 days / 1 night, Araku and Lambasingi', 46000),
        ('3 days / 2 nights, Vizag and Araku', 54000), ('3 days / 2 nights, Araku and Lambasingi', 66000),
        ('5 days / 4 nights, Vizag, Araku and Lambasingi', 95000))),
    ('araku-hotels-and-stays', PER_ROOM_NIGHT, STAY_BASIS, False, _options(
        ('Tribal Heritage Guest House (guest house)', 1800), ('Ananthagiri Hill Camp (camp stay)', 2100),
        ('Hotel Rajadhani Grand (AC hotel)', 2400), ('Apple Resorts (hill resort)', 2500),
        ('Borra Caves Lodge (nature lodge)', 2900), ('Padmapuram Garden Stay (garden resort)', 3600))),
    ('lambasingi-hotels-and-stays', PER_ROOM_NIGHT, STAY_BASIS, False, _options(
        ('Cool Breeze Guest Inn (budget inn)', 1500), ('Hilltop Camp Cottages (cottage camp)', 2200),
        ('Forest Edge Eco Stay (eco resort)', 2700), ('Sunrise Viewpoint Lodge (view lodge)', 2800),
        ('Lambasingi Mist Resort (hill resort)', 3400), ('Apple Orchard Cottages (cottage stay)', 4100))),
    ('vizag-hotels-and-stays', PER_ROOM_NIGHT, STAY_BASIS, False, _options(
        ('Station Transit Lodge (transit hotel, by the railway station)', 1400), ('Highway Comfort Inn (budget hotel, NH16)', 1600),
        ('MVP Grand Hotel (city hotel, MVP Colony)', 2200), ('Bayview Beach Resort (beach resort, RK Beach)', 2800),
        ('Yarada Hill Retreat (boutique stay, Yarada)', 3500), ('Dolphin Bay Suites (premium suite, Beach Road)', 4200))),
    ('maredumilli-hotels-and-stays', PER_ROOM_NIGHT, STAY_BASIS, False, _options(
        ('Papikonda Nature Camp (nature camp)', 1700), ('Bamboo Hut Homestay (homestay)', 1900),
        ('River View Guest House (riverside stay)', 2200), ('Jalatarangini Eco Lodge (eco lodge)', 2900),
        ('Maredumilli Forest Resort (forest resort)', 3100), ('Green Canopy Resort (jungle resort)', 3800))),
]
