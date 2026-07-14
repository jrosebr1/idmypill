# import the necessary packages
from apps.gsdb_datalab.gsdb.schemas import PillShape
from apps.gsdb_datalab.gsdb.schemas import PillColor
import re


def round_or_other_shapes(query_shape):
    # check to see if the pill is round
    if query_shape == PillShape.ROUND.value:
        # wrap the shape as a list and return it
        return [query_shape]

    # otherwise, return all pill shapes that are *not* round
    return [s.value for s in PillShape if s.value != PillShape.ROUND.value]


def white_or_other_colors(query_colors):
    # initialize a list to store the colors the query has been expanded into,
    # then grab all non-white colors
    expanded_colors = []
    non_white_colors = [
        c.value for c in PillColor if c.value != PillColor.WHITE.value
    ]

    # loop over all colors in the query
    for query_color in query_colors:
        # check to see if the color is white
        if query_color == PillColor.WHITE.value:
            # add the white color to the expanded list
            expanded_colors.append(query_color)

        # otherwise, we are examining a non-white character
        else:
            # add all non-white colors to the expanded list
            expanded_colors.extend(non_white_colors)

    # convert the expanded colors to a set, thereby removing any duplicates,
    # and then back to a list
    return list(set(expanded_colors))


def clean_imprint(imprint):
    # pre-process the imprint by converting it to lowercase followed by
    # replacing all whitespace with a blank character
    return re.sub(
        pattern=r'\s+',
        repl="",
        string=imprint.lower()
    )


def preprocess_imprints(imprints, sep=""):
    # check to see if the imprints are a string, and if so, wrap in a list, so
    # we can use this method, then initialize the list of cleaned imprints
    imprints = [imprints] if type(imprints) is str else imprints
    cleaned_imprints = []

    # loop over the original imprints
    for imprint in imprints:
        # clean the imprint
        cleaned_imprints.append(clean_imprint(imprint))

    # return the cleaned imprint as a single string
    return sep.join(cleaned_imprints)
