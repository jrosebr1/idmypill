# import the necessary packages
from django.contrib import admin
from . import models


class RxPillAdmin(admin.ModelAdmin):
    # allow the ID to be visible inside the Django admin
    readonly_fields = ("id", )


class RxPillImageAdmin(admin.ModelAdmin):
    # used to prevent Django from loading *all* 'RxPill' objects as a dropdown
    # list, causing the page to crash
    raw_id_fields = ("rxpill", )


# register the models
admin.site.register(models.RxName)
admin.site.register(models.RxPill, RxPillAdmin)
admin.site.register(models.RxPillImage, RxPillImageAdmin)
