# import the necessary packages
from .schemas import PillShape
from .schemas import PillAppearanceDetails

# define the name of the default shape (i.e., the "other category")
DEFAULT_SHAPE = "other"


class GSDBPillShapeSimplifier:

    # define a dictionary that maps GSDB pill shapes to valid shape names
    SHAPES_LOOKUP = {
        "triangular (3-sided)": str(PillShape.TRIANGLE),
        "rectangular": str(PillShape.RECTANGLE),
        "oblong": str(PillShape.OBLONG),
        "square": str(PillShape.SQUARE),
        "capsule": str(PillShape.CAPSULE),
        "clover": str(PillShape.CLOVER),
        "double circle": str(PillShape.DOUBLE_CIRCLE),
        "hexagonal (6-sided)": str(PillShape.HEXAGON),
        "tear": str(PillShape.TEAR),
        "diamond": str(PillShape.DIAMOND),
        "pentagonal (5-sided)": str(PillShape.PENTAGON),
        "trapezoid": str(PillShape.TRAPEZOID),
        "round": str(PillShape.ROUND),
        "octagon": str(PillShape.OCTAGON),
        "oval": str(PillShape.OVAL),
        "bullet": str(PillShape.BULLET),
    }

    def simplify(self, shape):
        # simplify the name of the shape, returning the default shape if the
        # supplied shape was not found
        return self.SHAPES_LOOKUP.get(shape.lower(), DEFAULT_SHAPE)


class PillAppearanceParser:

    def __init__(self, valid_colors):
        # store the set of valid color names a pill can take on
        self.valid_colors = valid_colors

        # instantiate our pill shape simplifier (used to prune down the
        # extraneous pill shapes from GSDB)
        self.shape_simplifier = GSDBPillShapeSimplifier()

    def parse(self, desc):
        # initialize the pill shape, colors, and imprints
        shape = None
        colors = []
        imprints = []

        # loop over all description elements
        for elem in self._preprocess_pill_desc(desc):
            # check to see if this is the shape element
            if self._is_shape(elem):
                # grab the shape and simplify it
                shape = elem.split("-shaped")[0]
                shape = self.shape_simplifier.simplify(shape)

            # check to see if this is part of the imprint
            elif self._is_imprint(elem):
                # extract the imprints, removing any occurrence of 'logo' from
                # the list (GSDB uses the text 'logo' to indicate the logo of
                # particular drug manufacturer, but since a logo can't be OCR'd
                # or read from free-text input, it doesn't serve us in our
                # identification and would just throw off our co-occurrence
                # matrix computations)
                imprint_side = [
                    s for s in elem.split(":")[-1].split(" ") if s != "logo"
                ]

                # ensure there is at least one entry in the imprints
                if len(imprint_side) > 0:
                    # update the imprints list
                    imprints.extend(imprint_side)

            # otherwise, we may be (1) examining the color, or (2) a totally
            # irrelevant element in the pill description
            else:
                # extract any potential colors from the element
                potential_colors = elem.split("-")

                # check to see if the color test passes
                if self._is_colors(potential_colors):
                    # update the colors list
                    colors.extend(potential_colors)

        # attempt to build the pill appearance details (will throw a validation
        # exception if any of the shape, colors, or imprints are invalid)
        return PillAppearanceDetails(
            shape=shape,
            colors=colors,
            imprints=imprints
        )

    @staticmethod
    def _is_shape(elem):
        # we're examining the shape element if the 'shaped' string occurs in
        # the element
        return "shaped" in elem

    @staticmethod
    def _is_imprint(elem):
        # we're examining an imprint element if 'side 1' or 'side 2' occurs in
        # the element
        return any(["side 1:" in elem, "side 2:" in elem])

    def _is_colors(self, potential_colors):
        # we're examining pill colors if all elements in the potential colors
        # list exists in our set of valid colors
        return all([c in self.valid_colors for c in potential_colors])

    @staticmethod
    def _preprocess_pill_desc(desc):
        # preprocess the pill description by breaking it into a series of
        # elements
        return [e.strip() for e in desc.lower().strip().split(",")]
