"""The photographs used on the site: the single source of truth for alt text, attribution and licence.

Every photo is a free-licence image from Wikimedia Commons (checked on its file page on 2026-10-25), cropped and
resized with scripts/optimize_photo.py into static/img/photos/<stem>-<width>.webp. None shows an identifiable person,
and none is a photo of a partner's vehicle, tour or property. Alt text describes only what the picture shows.

To add a photo: check its licence on the source page (CC0, CC BY or CC BY-SA only, never NC/ND), run the optimiser,
then add an entry here. The credits page and the admin dropdown pick it up automatically.
"""
from dataclasses import dataclass

CC0 = ('CC0 1.0', 'https://creativecommons.org/publicdomain/zero/1.0/')
BY_SA_4 = ('CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/')
BY_SA_2 = ('CC BY-SA 2.0', 'https://creativecommons.org/licenses/by-sa/2.0/')

ALLOWED_LICENCES = frozenset({CC0[0], BY_SA_4[0], BY_SA_2[0]})
COMMONS = 'https://commons.wikimedia.org/wiki/File:'
CHANGES = 'Cropped and resized; converted to WebP.'


@dataclass(frozen=True)
class Photo:
    key: str
    stem: str           # file name stem in static/img/photos/
    widths: tuple       # the pixel widths that exist on disk
    width: int          # size of the largest file (its aspect ratio sets width/height attributes)
    height: int
    alt: str
    title: str          # the Commons file title
    author: str
    licence: str
    licence_url: str
    source_url: str
    changes: str = CHANGES
    gallery: bool = False   # may appear in a page's photo strip
    place: str = 'araku-valley'   # Destination slug the photo shows (galleries stay on the page's own destination)

    @property
    def largest(self):
        return max(self.widths)


def _photo(key, widths, size, alt, title, author, licence, file_name, gallery=False, stem=None, place='araku-valley'):
    name, url = licence
    return Photo(
        key=key, stem=stem or key, widths=widths, width=size[0], height=size[1], alt=alt, title=title,
        author=author, licence=name, licence_url=url, source_url=COMMONS + file_name, gallery=gallery, place=place,
    )


BOTH = (800, 1600)

PHOTOS = (
    _photo('valley-dusk', BOTH, (1600, 893),
           'Farmland and a lone tree below blue hills at dusk in Araku Valley',
           'Lush Araku Valley', 'Jagannathsrs', BY_SA_4, 'Lush_Araku_Valley.jpg'),
    _photo('rainbow-hills', BOTH, (1600, 1200),
           'A rainbow over forested hills above a village in Araku Valley',
           'Rainbow on the Araku Valley', 'Maina Tudu', CC0, 'Rainbow_on_the_Araku_Valley.jpg', gallery=True),
    _photo('misty-pines', BOTH, (1600, 1160),
           'Tall pine trees in morning mist near Araku',
           'Pine trees at Araku', 'Drashokk', BY_SA_4, 'Pine_trees_at_Araku.jpg', gallery=True),
    _photo('galikonda-view', BOTH, (1600, 720),
           'Cloud over green hills and a valley, seen from the Galikonda viewpoint in Araku Valley',
           'Araku Valley from Galikonda View Point 01', 'Pratishkhedekar', BY_SA_4,
           'Araku_Valley_from_Galikonda_View_Point_01.jpg'),
    _photo('plantation', BOTH, (1600, 857),
           'Tall trees with pepper vines climbing their trunks in a shaded plantation in Araku Valley',
           'Araku Valley coffee plantations', 'Tarunsamanta', BY_SA_4, 'Araku_Valley_coffee_plantations.jpg',
           gallery=True),
    _photo('borra-caves', (800,), (800, 597),
           'Coloured lights and a skylight inside a limestone cave at Borra Caves',
           'Borra Caves with Lights', 'Alphakilo9', BY_SA_4, 'Borra_Caves_with_Lights.jpg', gallery=True),
    _photo('waterfall', (800,), (800, 531),
           'A small waterfall in green forest beside the ghat road to Araku',
           'Waterfall in eastern ghats 01', 'Drashokk (Dr Ashok Kolluru)', BY_SA_4, 'Waterfall_in_eastern_ghats_01.jpg',
           gallery=True),
    _photo('valley-road', BOTH, (1600, 1112),
           'A quiet road through green hills in Araku Valley',
           'A view of Araku Valley hill station in Andhra Pradesh', 'Billjones94', BY_SA_4,
           'A_view_of_Araku_Valley_hill_station_in_Andhra_Pradesh.jpg'),
    _photo('terraced-hills', BOTH, (1600, 1067),
           'Hazy blue hills with terraced fields in Araku Valley',
           'Araku Valley scenic view 02', 'roadconnoisseur', BY_SA_2, 'Araku_Valley_scenic_view_02.jpg',
           gallery=True),
    # Lambasingi and Vizag (added 2026-10-25; licences checked on the file pages)
    _photo('lambasingi-valley', BOTH, (1600, 1008),
           'A stream through grassland below forested hills near Lambasingi',
           'Valley near lambasinghi', 'IM3847', BY_SA_4, 'Valley_near_lambasinghi.jpg',
           gallery=True, place='lambasingi'),
    _photo('lambasingi-clouds', BOTH, (1600, 888),
           'Morning clouds filling the valleys below hills near Lambasingi',
           'Lambasinghi on a cloudy day', 'eclicks_by_bunny', BY_SA_4, 'Lambasinghi_on_a_cloudy_day.jpg',
           gallery=True, place='lambasingi'),
    _photo('kailasagiri-coast', BOTH, (1600, 631),
           'Green hills running down to the Bay of Bengal coast, seen from Kailasagiri in Visakhapatnam',
           'Kailasagiri hill and Bay of Bengal', 'IM3847', BY_SA_4, 'Kailasagiri_hill_and_Bay_of_Bengal.jpg',
           gallery=True, place='vizag'),
    _photo('rushikonda-beach', BOTH, (1600, 756),
           'Aerial view of waves breaking on rocks and sand at Rushikonda beach, Visakhapatnam',
           'Aerial view of Rushikonda beach', 'iMahesh', BY_SA_4, 'Aerial_view_of_Rushikonda_beach.jpg',
           gallery=True, place='vizag'),
    # Vanjangi and Maredumilli (added 2026-10-25; licences checked on the Commons file pages). The Vanjangi sunrise photo was
    # cropped to the sky and clouds because the full frame shows identifiable people.
    _photo('vanjangi-hills', BOTH, (1600, 742),
           'Clouds filling the valleys between green hills, seen from the Vanjangi hills near Paderu',
           'Vanjangi hills - paderu - andhrapradesh (4)', 'Muralikrishna m', BY_SA_4,
           'Vanjangi_hills_-_paderu_-_andhrapradesh_(4).jpg', gallery=True, place='vanjangi'),
    _photo('vanjangi-sunrise', BOTH, (1600, 640),
           'The sun rising above a sea of clouds, seen from the Vanjangi hilltop',
           'Sunrise from the Vanjangi hill top', 'iMahesh', BY_SA_4, 'Sunrise_from_the_Vanjangi_hill_top.jpg',
           gallery=True, place='vanjangi'),
    _photo('maredumilli-falls', BOTH, (1600, 841),
           'Water tumbling over mossy boulders in a forest stream at Maredumilli',
           'MAREDUMILLI - waterfalls', 'S. Sri Harsha', BY_SA_4, 'MAREDUMILLI_-_waterfalls.jpg',
           gallery=True, place='maredumilli'),
    _photo('maredumilli-forest', BOTH, (1600, 854),
           'Sunlit trees and climbing vines in the forest at Maredumilli',
           'MAREDUMILLI - forest area', 'S. Sri Harsha', BY_SA_4, 'MAREDUMILLI_-_forest_area.jpg',
           gallery=True, place='maredumilli'),
)

BY_KEY = {photo.key: photo for photo in PHOTOS}

@dataclass(frozen=True)
class Highlight:
    """A homepage "Explore" tile: a place or theme of the region, shown with one registry photo.

    Labels and blurbs state general, checkable facts about the area only; no prices, ratings or partner claims.
    """
    key: str
    label: str
    blurb: str

    @property
    def photo(self):
        return BY_KEY[self.key]


HIGHLIGHTS = (
    Highlight('plantation', 'Coffee plantations', 'Shade-grown coffee and pepper on the hill slopes.'),
    Highlight('borra-caves', 'Borra Caves', 'Limestone caverns in the Ananthagiri hills, on the Vizag side of Araku.'),
    Highlight('galikonda-view', 'Viewpoints', 'Hilltop lookouts with wide views across the valley.'),
    Highlight('waterfall', 'Waterfalls', 'Streams and small falls along the ghat road, fullest after the monsoon.'),
    Highlight('lambasingi-clouds', 'Lambasingi mornings', 'On cool mornings, clouds often settle in the valleys below the hills.'),
    Highlight('rushikonda-beach', 'Vizag beaches', 'Rushikonda and other beaches along the Visakhapatnam coast.'),
)

DEFAULT_HERO = 'valley-dusk'
# Used for a page that has no hero_image of its own, by page type.
DEFAULT_FOR_TYPE = {
    'home': 'valley-dusk', 'package': 'rainbow-hills', 'cab': 'valley-road', 'guide': 'misty-pines',
    'stay': 'terraced-hills', 'article': 'galikonda-view',
}


def get(key):
    """The Photo for a key, or None."""
    return BY_KEY.get(key)


def exists(key):
    return key in BY_KEY


def choices():
    """(key, label) pairs for the admin dropdown."""
    return [(photo.key, f'{photo.key} - {photo.alt}') for photo in PHOTOS]


def gallery(exclude=(), limit=4, place=None):
    """Photos for a page's strip. With a place, only photos of that destination; fewer than two means no strip."""
    items = [p for p in PHOTOS if p.gallery and p.key not in exclude and (place is None or p.place == place)]
    return items[:limit] if len(items) >= 2 else []
