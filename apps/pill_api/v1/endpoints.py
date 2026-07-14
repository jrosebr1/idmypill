# import the necessary packages
from django.conf import settings
from django.template.loader import render_to_string
from ninja import NinjaAPI
from apps.gsdb_datalab.models import RxPill
from apps.pill_id.identification import CoOccurrenceSearch
from apps.pill_api.models import APIKey
from apps.pill_api.models import APILog
from .schemas import PillIDRequest
from .schemas import PillIDResult
from .schemas import PillIDResponse
from .schemas import PillInfoRequest
from .schemas import PillInfoResponse
from .security import APIKeyAuth
import pickle
import json

# instantiate the API and authentication
api = NinjaAPI()
api_key = APIKeyAuth()

# try to load the co-occurrence matrix from disk
try:
    coo_matrix = pickle.loads(open(settings.COO_MATRIX_PATH, "rb").read())

# the co-occurrence matrix could not be found, so initialize it as an empty
# dictionary
except FileNotFoundError:
    coo_matrix = {}


@api.post(path="/id_pill/", response=PillIDResponse, auth=api_key)
def id_pill(request, data: PillIDRequest):
    # ensure we're performing authentication via an API key
    assert isinstance(request.auth, APIKey)

    # grab all pills from the database, then initialize our results list
    rxpills = RxPill.get_all_pills()
    response = []

    # build the query shapes, colors, and imprints
    query_shapes = str(data.shape)
    query_colors = [str(c) for c in data.colors]
    query_imprints = data.imprints

    # perform the search
    pill_searcher = CoOccurrenceSearch(rxpills, coo_matrix)
    search_results = pill_searcher.search(
        query_shapes,
        query_colors,
        query_imprints
    )

    # loop over the search results
    for (i, score) in search_results:
        # build the result
        result = PillIDResult(
            score=score,
            name=str(rxpills[i].name),
            ndc=rxpills[i].ndc,
            shape=rxpills[i].shape,
            colors=rxpills[i].colors,
            imprints=rxpills[i].imprints
        )
        response.append(result)

    # construct the response, consisting of the list of results
    response = PillIDResponse(results=response)

    # log the request and response
    api_log = APILog(
        api_key=request.auth,
        request=json.dumps(data.to_json()),
        response=json.dumps(response.to_json())
    )
    api_log.save()

    # return the list of results
    return response


@api.post(path="/pill_info/", response=PillInfoResponse, auth=api_key)
def pill_info(request, data: PillInfoRequest):
    # ensure we're performing authentication via an API key
    assert isinstance(request.auth, APIKey)

    # lookup the pills in the database, ensuring that the original order of
    # the NDCs list is preserved in the query, then initialize our context
    # dictionary
    rxpills = RxPill.get_drugs_by_ndcs(data.ndcs, preserve_order=True)
    ctx = {"drugs": []}

    # loop over the pills
    for rxpill in rxpills:
        # grab the image URL associated with the pill (if such an image exists
        # in the database)
        image_url = rxpill.image.first().image_url(use_prod=True) \
            if rxpill.image.exists() else None

        # update the context dictionary
        ctx["drugs"].append({
            "name": str(rxpill.name),
            "image_url": image_url,
            "ndc": rxpill.ndc,
            "dea_classification": rxpill.dea_classification,
            "shape": rxpill.shape,
            "colors": rxpill.colors,
            "imprints": rxpill.imprints,
        })

    # render the template
    rendered = render_to_string(
        template_name="pill_api/v1/pill_info_response.md",
        context=ctx
    )

    # return the table of data as a string
    return PillInfoResponse(response=rendered)
