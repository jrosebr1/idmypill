# import the necessary packages
from apps.gsdb_datalab.gsdb.schemas import PillShape
from apps.gsdb_datalab.gsdb.schemas import PillColor
from ninja import Schema
from typing import List


class PillIDRequest(Schema):
    shape: PillShape
    colors: List[PillColor]
    imprints: List[str]

    def to_json(self):
        # return a JSON-serializable dictionary of the request
        return {
            "shape": str(self.shape),
            "colors": [str(c) for c in self.colors],
            "imprints": self.imprints,
        }


class PillIDResult(Schema):
    score: float
    name: str
    ndc: str
    shape: PillShape
    colors: List[PillColor]
    imprints: List[str]

    def to_json(self):
        # return a JSON-serializable dictionary of the result
        return {
            "score": self.score,
            "name": self.name,
            "ndc": self.ndc,
            "shape": str(self.shape),
            "colors": [str(c) for c in self.colors],
            "imprints": self.imprints,
        }


class PillIDResponse(Schema):
    results: List[PillIDResult]

    def to_json(self):
        # return a JSON-serializable dictionary of the response
        return [r.to_json() for r in self.results]


class PillInfoRequest(Schema):
    ndcs: List[str]


class PillInfoResponse(Schema):
    response: str
