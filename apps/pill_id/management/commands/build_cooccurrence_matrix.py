# USAGE
# python manage.py build_cooccurrence_matrix

# import the necessary packages
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.pill_id.identification import CoOccurrenceMatrixBuilder
from apps.gsdb_datalab.models import RxPill
import pandas as pd
import pickle
import os


class Command(BaseCommand):

    # explain what this script does
    help = "Computes co-occurrence matrix for shape, color, and imprint"

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
        # check to see if the co-occurrence matrix has already been computed
        if os.path.exists(options["matrix"]):
            # if so, there's no need to re-compute it, so return early
            self.stdout.write("* co-occurrence matrix already computed")
            return

        # initialize the list of output rows in our dataframe
        rows = []

        # loop over all pills in the database
        for rxpill in RxPill.get_all_pills(to_list=False):
            # construct the row, consisting of the pill shape, colors, and
            # imprints, then update the list of rows
            row = [
                rxpill.shape,
                " ".join(rxpill.colors),
                rxpill.concat_imprints(),
            ]
            rows.append(row)

        # construct the dataframe, dropping any rows where the shape or color
        # is empty
        df = pd.DataFrame(rows, columns=["Shape", "Colors", "Imprints"])
        df = df.drop(df[df["Shape"] == "none"].index)
        df = df.drop(df[df["Colors"].str.len() == 0].index)

        # build the co-occurrence matrix
        coo_builder = CoOccurrenceMatrixBuilder(df)
        coo_matrix = coo_builder.compute()

        # save the co-occurrence matrix to disk
        with open(options["matrix"], "wb") as f:
            f.write(pickle.dumps(coo_matrix))
