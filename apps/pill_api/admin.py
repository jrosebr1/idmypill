# import the necessary packages
from django.contrib import admin
from . import models


# register the models
admin.site.register(models.APIKey)
admin.site.register(models.APILog)
