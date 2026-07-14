# import the necessary packages
from ninja import Schema
from typing import Optional
from typing import List
from enum import Enum


class CaseInsensitiveEnum(Enum):

    def __new__(cls, value: str):
        # create a new instance of our class, then explicitly convert the
        # value to lowercase
        obj = object.__new__(cls)
        obj._value_ = value.lower()

        # return the object instance
        return obj

    @classmethod
    def _missing_(cls, value: str):
        # in the event no match is found, we'll call the parent missing method,
        # thereby making our implementation consistent with the rest of the
        # enum class
        missing = super()._missing_(value)

        # if the value is invalid, return the missing value
        if not value:
            return missing

        # loop over each member of the enum
        for member in cls:
            # check to see if the current member and value match
            if member.value == value.lower().strip():
                # return the current member
                return member

        # return the missing value
        return missing

    def __str__(self):
        # return the string value
        return self.value


class PillShape(CaseInsensitiveEnum):
    ROUND = "round"
    CAPSULE = "capsule"
    OBLONG = "oblong"
    OVAL = "oval"
    TRIANGLE = "triangle"
    RECTANGLE = "rectangle"
    SQUARE = "square"
    DIAMOND = "diamond"
    PENTAGON = "pentagon (5 sided)"
    HEXAGON = "hexagon (6 sided)"
    OCTAGON = "octagon (8 sided)"
    CLOVER = "clover"
    DOUBLE_CIRCLE = "double circle"
    TEAR = "tear"
    TRAPEZOID = "trapezoid"
    BULLET = "bullet"


class PillColor(CaseInsensitiveEnum):
    WHITE = "white"
    YELLOW = "yellow"
    ORANGE = "orange"
    COLORLESS = "colorless"
    RUST = "rust"
    GOLD = "gold"
    BLUE = "blue"
    PINK = "pink"
    BEIGE = "beige"
    MAROON = "maroon"
    RED = "red"
    AMBER = "amber"
    BROWN = "brown"
    GREEN = "green"
    GRAY = "gray"
    TAN = "tan"
    PURPLE = "purple"
    PEACH = "peach"
    BLACK = "black"


class PillAppearanceDetails(Schema):
    shape: PillShape
    colors: List[PillColor]
    imprints: List[str]

    def to_json(self):
        # return a JSON-serializable dictionary of the pill appearance
        return {
            "shape": str(self.shape),
            "colors": [str(c) for c in self.colors],
            "imprints": self.imprints,
        }


class DrugVersion(Schema):
    drug_id: int
    version: int
    pill_appearance: PillAppearanceDetails
    image_filename: Optional[str]


class DrugProductInformation(Schema):
    ndc: str
    name: str
    dea_classification: Optional[str]
