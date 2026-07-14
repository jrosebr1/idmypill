# import the necessary packages
from ninja.security import APIKeyHeader
from apps.pill_api.models import APIKey


class APIKeyAuth(APIKeyHeader):
    # indicate that the API key will be part of the header
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        # check to see if the API key is valid
        try:
            return APIKey.objects.get(api_key=key)

        # a matching API key entry does not exist
        except APIKey.DoesNotExist:
            pass
