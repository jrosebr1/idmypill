# import the necessary packages
from django.db import models


class APIKey(models.Model):
    # define the model schema
    api_key = models.CharField(max_length=32, db_index=True)

    def __str__(self):
        # return the API key
        return self.api_key

    class Meta:
        verbose_name = "APIKey"
        verbose_name_plural = "APIKeys"


class APILog(models.Model):
    # define the model schema
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE)
    request = models.TextField()
    response = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return the name of the API key and the date of the request as the
        # string representation of the object
        return " - ".join([str(self.api_key), str(self.date_added)])

    class Meta:
        verbose_name = "APILog"
        verbose_name_plural = "APILogs"
