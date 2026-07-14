# USAGE
# python manage.py build_production_images

# import the necessary packages
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.gsdb_datalab.models import RxPillImage
from tqdm import tqdm
import shutil


class Command(BaseCommand):

    # define the GSDB data root directory and images paths
    GSDB_DATA_PATH = settings.GSDB_DATA_DIR
    GSDB_IMAGES_PATH = settings.GSDB_IMAGES_PATH
    GSDB_PROD_IMAGES_PATH = settings.GSDB_PROD_IMAGES_PATH

    # explain what this script does
    help = "Creates directory of production pill images"

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

        # check to see if the output images directory does not exist
        if not self.GSDB_PROD_IMAGES_PATH.exists():
            # log the error and exit
            self.stdout.write(
                "* ERROR: images output directory does not exist: {}".format(
                    self.GSDB_PROD_IMAGES_PATH
                )
            )
            return

        # grab all pill images and construct the iterator
        rximages = RxPillImage.objects.all()
        rximages = tqdm(rximages, total=len(rximages)) \
            if options["verbose"] else rximages

        # loop over the images
        for rximage in rximages:
            # clone the image to its output directory
            self._copy_image(
                self.GSDB_IMAGES_PATH,
                self.GSDB_PROD_IMAGES_PATH,
                rximage
            )

    @staticmethod
    def _copy_image(base_input_path, base_output_path, rximage):
        # build the path to the input and output images, then copy the image
        shutil.copy2(
            base_input_path / rximage.gsdb_image_filename,
            base_output_path / rximage.prod_image_filename
        )
