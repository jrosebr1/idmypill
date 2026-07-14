# import the necessary packages
from pathlib import Path
from django.db.models import Case
from django.db.models import When
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from .gsdb.helpers import get_short_hash
import json


class RxName(models.Model):
    # define the model schema
    name = models.CharField(max_length=255)

    def __str__(self):
        # return the name of the drug
        return self.name

    class Meta:
        verbose_name = "RxName"
        verbose_name_plural = "RxName"


class RxPill(models.Model):
    # define the model schema
    name = models.ForeignKey(RxName, on_delete=models.CASCADE)
    ndc = models.CharField(max_length=16, db_index=True)
    drug_data = models.TextField()
    dea_classification = models.CharField(max_length=16, null=True, blank=True)
    gsdb_item_id = models.IntegerField(db_index=True)
    gsdb_item_version = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        # call the parent constructor
        super().__init__(*args, **kwargs)

        # parse the drug JSON blob
        self._drug_data_parsed = json.loads(self.drug_data) \
            if self.drug_data else {}

    @property
    def shape(self):
        # return the shape of the pill
        return self._drug_data_parsed.get("shape", None)

    @property
    def colors(self):
        # return the colors of the pill
        return self._drug_data_parsed.get("colors", [])

    @property
    def imprints(self):
        # return the imprints on the pill
        return self._drug_data_parsed.get("imprints", [])

    def concat_imprints(self, sep=" "):
        # concatenate and return the imprints
        return sep.join(self.imprints)

    @staticmethod
    def drug_exists(ndc, version):
        # if the combination of NDC and version exists in our database, then
        # we already have record of this drug
        return RxPill.objects.filter(
            ndc=ndc,
            gsdb_item_version=version
        ).count() > 0

    @staticmethod
    def get_drugs_by_ndcs(ndcs, preserve_order=True):
        # grab the drugs with the supplied NDCs, making sure to pull any images
        # associated with the pills
        rxpills = RxPill.objects.filter(ndc__in=ndcs).prefetch_related("image")

        # check to see if the original order of the NDC list should be
        # preserved
        if preserve_order:
            # associate each NDC with its original position in the list, then
            # apply the custom ordering
            ordering = Case(
                *[When(ndc=ndc, then=pos) for (pos, ndc) in enumerate(ndcs)]
            )
            rxpills = rxpills.order_by(ordering)

        # return the drugs
        return rxpills

    @staticmethod
    def get_all_pills(to_list=True):
        # grab all pills in the database, ensuring the pills are ordered by
        # their ID in ascending order
        rxpills = RxPill.objects.all().order_by("id")

        # return the pills, converting to a list of necessary
        return list(rxpills) if to_list else rxpills

    def __str__(self):
        # construct a string representation of the pill
        return " - ".join([
            str(self.id),
            self.ndc,
            "v{}".format(str(self.gsdb_item_version)),
            str(self.name),
        ])

    class Meta:
        verbose_name = "RxPill"
        verbose_name_plural = "RxPills"


class RxPillImage(models.Model):
    # define the model schema
    rxpill = models.ForeignKey(
        RxPill,
        related_name="image",
        on_delete=models.CASCADE
    )
    gsdb_image_filename = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    prod_image_filename = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    date_added = models.DateTimeField(auto_now_add=True)

    def image_url(self, use_prod=True):
        # grab either the GSDB or the production image filename, depending on
        # the supplied value
        filename = self.prod_image_filename if use_prod \
            else self.gsdb_image_filename

        # if the image filename is None, return the same
        if filename is None:
            return None

        # otherwise, build and return the full image URL
        return "".join([settings.PILL_IMAGES_URL, filename])

    def __str__(self):
        # return a string representation of the pill image
        return " - ".join([
            str(self.rxpill.id),
            self.rxpill.ndc,
            "v{}".format(str(self.rxpill.gsdb_item_version)),
            self.gsdb_image_filename
        ])

    class Meta:
        verbose_name = "RxPillImage"
        verbose_name_plural = "RxPillImages"


@receiver(models.signals.pre_save, sender=RxPillImage)
def rxpillimage_pre_save(sender, instance, *args, **kwargs):
    # check to see if a GSDB filename was provided
    if instance.gsdb_image_filename:
        # to form the production image filename we'll compute a hash over
        # the GSDB filename, then combine it with the original image
        # extension
        instance.prod_image_filename = "".join([
            get_short_hash(instance.gsdb_image_filename),
            Path(instance.gsdb_image_filename).suffix
        ])
