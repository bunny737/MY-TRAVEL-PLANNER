from datetime import date

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.core.models import ContentPage, Partner
from apps.core.seed.prices import DEFAULT_QUOTED_ON, PRICES

UNDATED_NOTE = (
    'PRICE: the partner site showed this price with no date; we used {when} (owner decision 2026-10-25). Ask the partner to confirm it still holds.'
)
DATED_NOTE = 'PRICE: copied from a partner page that printed "Prices last updated: 24 October 2026". Confirm it still holds.'


class Command(BaseCommand):
    help = (
        'Fill the dated partner "from" prices and option lists on the launch package and stay pages '
        '(docs/research/partner-facts-2026-10.md). By default it only fills pages that have no price yet and never overwrites '
        'one you entered. With --refresh it also rewrites pages whose price came from this partner. Safe to run twice. '
        'Prices hide themselves on the site after PRICE_MAX_AGE_DAYS.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--partner', required=True, help='business_name of the Partner row that gave the quotes (create it in admin first)')
        parser.add_argument('--quoted-on', default=DEFAULT_QUOTED_ON, help=f'date of the quote, YYYY-MM-DD (default {DEFAULT_QUOTED_ON})')
        parser.add_argument('--refresh', action='store_true', help='rewrite pages already priced by this same partner to match the data file')

    def handle(self, *args, **options):
        try:
            partner = Partner.objects.get(business_name=options['partner'])
        except Partner.DoesNotExist:
            raise CommandError(f'No partner called "{options["partner"]}". Add it in admin (Partners) first.')
        try:
            quoted_on = date.fromisoformat(options['quoted_on'])
        except ValueError:
            raise CommandError('--quoted-on must look like 2026-10-24')

        done = skipped = 0
        for slug, unit, basis, dated, option_rows in PRICES:
            page = ContentPage.objects.filter(slug=slug).first()
            if page is None:
                self.stdout.write(f'Page "{slug}" does not exist; skipped (run seed_site_content first).')
                skipped += 1
                continue
            if page.price_from is not None and not (options['refresh'] and page.price_partner_id == partner.pk):
                self.stdout.write(f'Page "{slug}" already has a price; left unchanged.')
                skipped += 1
                continue
            already_noted = 'PRICE:' in page.internal_notes
            page.price_from = min(amount for _, amount in option_rows)
            page.price_unit, page.price_basis = unit, basis
            page.price_quoted_on, page.price_partner = quoted_on, partner
            page.price_options = '\n'.join(f'{label} | {amount}' for label, amount in option_rows) if len(option_rows) > 1 else ''
            if not already_noted:
                note = DATED_NOTE if dated else UNDATED_NOTE.format(when=quoted_on.strftime('%d %B %Y').lstrip('0'))
                page.internal_notes = f'{page.internal_notes} {note}'.strip()
            try:
                page.full_clean()
            except ValidationError as error:
                raise CommandError(f'"{slug}": {"; ".join(error.messages)}')
            page.save()
            done += 1
            self.stdout.write(f'Set {page.price_from} for "{slug}" ({len(option_rows)} option(s), quote dated {quoted_on}).')
        self.stdout.write(self.style.SUCCESS(f'{done} price(s) set, {skipped} skipped.'))
