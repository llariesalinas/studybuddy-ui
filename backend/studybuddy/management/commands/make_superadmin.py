from getpass import getpass

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from studybuddy.models import UserProfile


def build_profile_defaults(user):
    display_name = (
        user.get_full_name().strip()
        or user.email.split('@', 1)[0]
        or user.username
        or 'SuperAdmin'
    )
    name_parts = display_name.replace('.', ' ').replace('_', ' ').split()

    return {
        'fname': (user.first_name or (name_parts[0] if name_parts else 'SuperAdmin'))[:100],
        'mname': '',
        'lname': (user.last_name or (' '.join(name_parts[1:]) if len(name_parts) > 1 else 'User'))[:100],
        'role': 'SuperAdmin',
        'profile_completed': True,
        'is_domain_exempt': True,
        'is_suspended': False,
    }


class Command(BaseCommand):
    help = 'Promote an existing Django user to the StudyBuddy SuperAdmin app role.'

    def add_arguments(self, parser):
        parser.add_argument('email', help='Email address of the user to promote.')
        parser.add_argument(
            '--create',
            action='store_true',
            help='Create the Django user first if no account exists for this email.',
        )
        parser.add_argument('--first-name', default='', help='First name to use when creating the user.')
        parser.add_argument('--last-name', default='', help='Last name to use when creating the user.')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        user = User.objects.filter(username__iexact=email).first()
        email_matches = User.objects.filter(email__iexact=email)

        if user is None:
            user = email_matches.first()

        if user is None:
            if not options['create']:
                raise CommandError(
                    f'No user found with email "{email}". '
                    'Register the user first, or rerun with --create.'
                )

            password = getpass('Password: ')
            password_again = getpass('Password (again): ')

            if password != password_again:
                raise CommandError('Passwords do not match.')

            try:
                validate_password(password)
            except ValidationError as exc:
                raise CommandError('\n'.join(exc.messages)) from exc

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=options['first_name'].strip(),
                last_name=options['last_name'].strip(),
            )
        elif email_matches.count() > 1:
            self.stdout.write(
                self.style.WARNING(
                    f'Found {email_matches.count()} users with email "{email}". '
                    f'Promoting login username match user_id={user.id}.'
                )
            )

        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults=build_profile_defaults(user),
        )

        if not created:
            profile.role = 'SuperAdmin'
            profile.profile_completed = True
            profile.is_domain_exempt = True
            profile.is_suspended = False
            profile.save(update_fields=[
                'role',
                'profile_completed',
                'is_domain_exempt',
                'is_suspended',
                'updated_at',
            ])

        action = 'Created profile and promoted' if created else 'Promoted'
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} {user.email} to SuperAdmin.'
            )
        )
