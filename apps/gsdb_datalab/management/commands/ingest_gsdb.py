# USAGE
# python manage.py ingest_gsdb

# import the necessary packages
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.gsdb_datalab.gsdb import GSDBLoader
from apps.gsdb_datalab.models import RxName
from apps.gsdb_datalab.models import RxPill
from apps.gsdb_datalab.models import RxPillImage
from collections import Counter
from tqdm import tqdm
import json


class Command(BaseCommand):

    # define the GSDB data root directory and images path
    GSDB_DATA_PATH = settings.GSDB_DATA_DIR
    GSDB_IMAGES_PATH = settings.GSDB_IMAGES_PATH

    # define meta task counts for number of drugs added to the database
    # and ignored (due to the drug *already* existing in the database)
    NUM_DRUGS_ADDED = "num_drugs_added"
    NUM_DRUGS_SKIPPED = "num_drugs_skipped"

    # explain what this script does
    help = "Parses GSDB data and inserts drugs into database"

    def __init__(self):
        # call the parent constructor
        super().__init__()

        # initialize a task counter to count the number of drugs processed
        self.task_counter = Counter({
            self.NUM_DRUGS_ADDED: 0,
            self.NUM_DRUGS_SKIPPED: 0,
        })

    def add_arguments(self, parser):
        # verbosity setting
        parser.add_argument(
            "-p",
            "--verbose",
            type=int,
            default=1,
            help="verbosity setting"
        )

    def handle(self, *args, **options):
        # check if the input images directory does not exist
        if not self.GSDB_IMAGES_PATH.exists():
            # log the error and exit
            self.stdout.write(
                "* ERROR: images input directory does not exist: {}".format(
                    self.GSDB_IMAGES_PATH
                )
            )
            return

        # instantiate the GSDB data loader and iterator
        data_loader = GSDBLoader(self.GSDB_DATA_PATH, self.GSDB_IMAGES_PATH)
        data_loader = tqdm(data_loader, total=data_loader.total_drugs()) \
            if options["verbose"] > 0 else data_loader

        # loop over all rows in the loader
        for (product_info, drug_versions) in data_loader:
            # check to see if the drug should be skipped
            if any([product_info is None, drug_versions is None]):
                continue

            # loop over the drug versions
            for drug in drug_versions:
                # check to see if the drug NDC and version *already* exists in
                # the database
                if RxPill.drug_exists(product_info.ndc, drug.version):
                    # increment the number of tasks skipped, then keep looping
                    self.task_counter[self.NUM_DRUGS_SKIPPED] += 1
                    continue

                # save the drug information to the database
                rxpill = RxPill(
                    ndc=product_info.ndc,
                    name=self._get_drug_name(product_info.name),
                    drug_data=json.dumps(drug.pill_appearance.to_json()),
                    dea_classification=product_info.dea_classification,
                    gsdb_item_id=drug.drug_id,
                    gsdb_item_version=drug.version,
                )
                rxpill.save()

                # check to see if an image filename exists for the drug
                if drug.image_filename is not None:
                    # save the pill image to the database
                    rximage = RxPillImage(
                        rxpill=rxpill,
                        gsdb_image_filename=drug.image_filename
                    )
                    rximage.save()

                # increment the number of drugs successfully added to the
                # database
                self.task_counter[self.NUM_DRUGS_ADDED] += 1

        # loop over the final task counts
        for (task_name, task_count) in self.task_counter.items():
            # display statistics on the number of tasks
            self.stdout.write("* {}: {}".format(task_name, task_count))

    @staticmethod
    def _get_drug_name(drug_name):
        # if the drug name already exists grab it from the database, otherwise
        # create it
        return RxName.objects.get_or_create(name=drug_name)[0]
