"""Plain-text formats for page content edited in Django admin.

Everything is stored as ordinary text and rendered escaped, so nothing an editor types can inject markup.
  * list fields (inclusions, exclusions): one item per line.
  * block fields (itinerary, FAQ): blocks separated by a blank line; the first line of a block is its heading
    (the day / the question), the remaining lines are its text.
  * body: paragraphs separated by a blank line.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Block:
    heading: str
    lines: tuple


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
