# USAGE
# python manage.py test_coo

# import the necessary packages
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.gsdb_datalab.models import RxPill
from apps.pill_id.identification import CoOccurrenceSearch
import pickle


class Command(BaseCommand):

    # explain what this script does
    help = "Test co-occurrence filtering"

    def add_arguments(self, parser):
        # path to output co-occurrence matrix
        parser.add_argument(
            "-m",
            "--matrix",
            type=str,
            default=settings.COO_MATRIX_PATH,
            help="path to output co-occurrence matrix"
        )

    def handle(self, *args, **options):
        # set the query information
        query_id = 1
        query_shape = "round"
        query_colors = ["yellow"]
        query_imprints = ["mylan"]

        # grab all pills from the database
        rxpills = RxPill.get_all_pills()

        # load the co-occurrence matrix from disk
        with open(options["matrix"], "rb") as f:
            coo_matrix = pickle.load(f)

        # perform the search
        pill_searcher = CoOccurrenceSearch(rxpills, coo_matrix)
        results = pill_searcher.search(
            query_shape,
            query_colors,
            query_imprints
        )
        print(results)
