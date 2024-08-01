from django.core.management.base import BaseCommand, CommandError
from Rotation.utils import update_database_config

class Command(BaseCommand):
    help = 'Update the database location'

    def add_arguments(self, parser):
        parser.add_argument('new_location', type=str, help='New database file location')

    def handle(self, *args, **options):
        new_location = options['new_location']
        if update_database_config(new_location):
            self.stdout.write(self.style.SUCCESS(f'Database location updated to {new_location}'))
            self.stdout.write(self.style.WARNING('Please restart the server for changes to take effect.'))
        else:
            raise CommandError('Failed to update database location')
