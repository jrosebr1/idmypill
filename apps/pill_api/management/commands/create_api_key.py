# USAGE
# python manage.py create_api_key
# python manage.py create_api_key --key my-custom-key

# import the necessary packages
from django.core.management.base import BaseCommand
from apps.pill_api.models import APIKey
import secrets


class Command(BaseCommand):

    # explain what this script does
    help = "Creates a new API key for authenticating against the pill API"

    def add_arguments(self, parser):
        # optionally allow the caller to supply a specific API key value
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            default=None,
            help="specific API key value to use (otherwise one is generated)"
        )

    def handle(self, *args, **options):
        # use the supplied key if one was provided, otherwise generate a random
        # 32-character key
        key = options["key"] or secrets.token_hex(16)

        # ensure the key fits within the database column
        if len(key) > 32:
            # the key is too long, exit
            self.stdout.write("* ERROR: API key must be <= 32 characters")
            return

        # check if the key already exists in the database
        if APIKey.objects.filter(api_key=key).exists():
            # the key already exists, exit
            self.stdout.write("* API key already exists: {}".format(key))
            return

        # create and save the API key
        APIKey.objects.create(api_key=key)

        # report the new key back to the caller
        self.stdout.write("* created API key: {}".format(key))
        self.stdout.write(
            "* send it in the 'X-API-Key' header on every API request"
        )
