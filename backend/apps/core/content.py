"""Plain-text formats for page content edited in Django admin.

Everything is stored as ordinary text and rendered escaped, so nothing an editor types can inject markup.
  * list fields (inclusions, exclusions): one item per line.
  * block fields (itinerary, FAQ): blocks separated by a blank line; the first line of a block is its heading
    (the day / the question), the remaining lines are its text.
  * body: paragraphs separated by a blank line. On guides and articles a body paragraph may also be a
    "## Heading" line or a "[photo: key]" line (see parse_article).
"""
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from django.utils.text import slugify


@dataclass(frozen=True)
class Block:
    heading: str
    lines: tuple


@dataclass(frozen=True)
class Segment:
    """One piece of an article body: kind is 'heading', 'photo' or 'paragraph'. `anchor` is set on headings."""
    kind: str
    text: str
    anchor: str = ''


PHOTO_LINE = re.compile(r'^\[photo:\s*([a-z0-9-]+)\s*\]$')


def _lines(text):
    return [line.strip() for line in (text or '').replace('\r\n', '\n').replace('\r', '\n').split('\n')]


def parse_list(text):
    return [line for line in _lines(text) if line]


def parse_paragraphs(text):
    """Blank-line separated paragraphs; single line breaks inside a paragraph are joined with a space."""
    paragraphs, current = [], []
    for line in _lines(text) + ['']:
        if line:
            current.append(line)
        elif current:
            paragraphs.append(' '.join(current))
            current = []
    return paragraphs


def parse_blocks(text):
    blocks, current = [], []
    for line in _lines(text) + ['']:
        if line:
            current.append(line)
        elif current:
            blocks.append(Block(heading=current[0], lines=tuple(current[1:])))
            current = []
    return blocks


def parse_article(text):
    """Split a guide/article body into headings, photos and paragraphs.

    A line starting with "## " is a heading, a line that is only "[photo: key]" is a photo from the licensed library, and
    anything else is paragraph text (same blank-line rules as parse_paragraphs). Heading anchors are unique within the body.
    """
    segments, seen = [], {}
    for paragraph in parse_paragraphs_keeping_lines(text):
        if paragraph.startswith('## ') and paragraph[3:].strip():
            title = paragraph[3:].strip()
            base = slugify(title) or 'section'
            seen[base] = seen.get(base, 0) + 1
            anchor = base if seen[base] == 1 else f'{base}-{seen[base]}'
            segments.append(Segment('heading', title, anchor))
            continue
        photo = PHOTO_LINE.match(paragraph)
        if photo:
            segments.append(Segment('photo', photo.group(1)))
        else:
            segments.append(Segment('paragraph', paragraph))
    return segments


def parse_paragraphs_keeping_lines(text):
    """Like parse_paragraphs, but a heading or photo line on its own always ends the paragraph before and after it."""
    paragraphs, current = [], []

    def flush():
        if current:
            paragraphs.append(' '.join(current))
            current.clear()

    for line in _lines(text) + ['']:
        if not line:
            flush()
        elif line.startswith('## ') or PHOTO_LINE.match(line):
            flush()
            paragraphs.append(line)
        else:
            current.append(line)
    return paragraphs


def parse_price_options(text):
    """Price option lines "label | amount" -> [(label, Decimal)]. Raises ValueError naming the first bad line.

    The amount is parsed as Decimal (never float) and must be finite and above zero; the label is at most 80 characters.
    """
    rows = []
    for line in parse_list(text):
        label, bar, amount = line.rpartition('|')
        label = label.strip()
        try:
            value = Decimal(amount.strip().replace(',', ''))
        except InvalidOperation:
            raise ValueError(line)
        if not bar or not label or len(label) > 80 or not value.is_finite() or value <= 0:
            raise ValueError(line)
        rows.append((label, value))
    return rows


def format_inr(amount):
    """₹ amount from a Decimal with Indian digit grouping (₹1,00,000). Whole rupees show no decimals. Never uses float."""
    amount = Decimal(amount)
    whole = amount == amount.to_integral_value()
    text = f'{abs(amount):.0f}' if whole else f'{abs(amount):.2f}'
    integer, _, fraction = text.partition('.')
    if len(integer) > 3:
        head, tail = integer[:-3], integer[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        integer = ','.join(groups + [tail])
    sign = '-' if amount < 0 else ''
    return f'{sign}₹{integer}' + (f'.{fraction}' if fraction else '')
