# USAGE
# python manage.py evaluate_search

# import the necessary packages
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.gsdb_datalab.models import RxPill
from apps.pill_id.identification import CoOccurrenceSearch
from apps.pill_id.identification.helpers import clean_imprint
from tqdm import tqdm
import pandas as pd
import pickle
import random


class Command(BaseCommand):

    # explain what this script does
    help = "Evaluates pill identification accuracy"

    def add_arguments(self, parser):
        # percentage of imprint characters to jitter
        parser.add_argument(
            "-i",
            "--imprint-jitter",
            type=float,
            default=-1,
            help="percentage of imprint characters to jitter"
        )

    def handle(self, *args, **options):
        # grab all pills from the database
        rxpills = RxPill.get_all_pills()

        # load the co-occurrence matrix from disk
        with open(settings.COO_MATRIX_PATH, "rb") as f:
            coo_matrix = pickle.load(f)

        # initialize the pill searcher
        pill_searcher = CoOccurrenceSearch(rxpills, coo_matrix)

        # initialize a list to store the search result positions, along with
        # a list to count the number of searches where the query index was
        # not found in the results
        found = []
        not_found = []

        # loop over all pills in the database
        for (q_idx, rxpill) in tqdm(enumerate(rxpills), total=len(rxpills)):
            # grab the pill imprint and preprocess it
            imprint_text = clean_imprint(rxpill.concat_imprints())

            # check to see if the imprint text should be jittered
            if options["imprint_jitter"] > 0:
                imprint_text = self._jitter_imprint(
                    imprint_text,
                    options["imprint_jitter"]
                )

            # perform the search, then extract the indexes of the search result
            # pills
            results = pill_searcher.search(
                rxpill.shape,
                rxpill.colors,
                imprint_text
            )
            result_idxs = [r[0] for r in results]

            # try to find the position of the query index in the search indexes
            try:
                # find the index (adding one since we are zero-index), then
                # update the list of positions
                found_idx = result_idxs.index(q_idx) + 1
                found.append(found_idx)

            # the query index does not exist in the search result indexes
            except ValueError:
                # update the indexes where the search failed with the query
                # index
                not_found.append(q_idx)

        # analyze the search result positions by computing statistics over them
        df = pd.DataFrame(found, columns=["Positions"])
        self.stdout.write(str(df.describe().T))

        # display the number of searches where the query index was not found in
        # the search results
        self.stdout.write("not_found: {}".format(len(not_found)))

    @staticmethod
    def _jitter_imprint(s, p):
        # compute the total number of characters to remove, then randomly
        # decide how many characters to remove from the front and end of
        # the string, respectively
        total_to_remove = int(len(s) * p)
        remove_start = random.randint(0, total_to_remove)
        remove_end = total_to_remove - remove_start

        # remove the characters from the start and end of the string
        return s[remove_start:-remove_end or None]
