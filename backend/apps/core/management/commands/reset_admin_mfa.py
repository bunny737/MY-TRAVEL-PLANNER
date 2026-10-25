from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django_otp.plugins.otp_totp.models import TOTPDevice


class Command(BaseCommand):
    help = ('Remove every authenticator of an admin user (lost phone). They set up a new one at their next admin '
            'sign-in, so sign in straight after running this.')

    def add_arguments(self, parser):
        parser.add_argument('username')

    def handle(self, *args, username, **options):
        user_model = get_user_model()
        user = user_model.objects.filter(**{user_model.USERNAME_FIELD: username}).first()
        if user is None:
            raise CommandError(f'No user called {username!r}.')
        removed, _ = TOTPDevice.objects.filter(user=user).delete()
        self.stdout.write(f'Removed {removed} authenticator(s) for {username}. '
                          'Sign in to the admin now to set up a new one.')
