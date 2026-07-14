# import the necessary packages
from tqdm import tqdm
import itertools


class CoOccurrenceMatrixBuilder:

    def __init__(self, df, delim="\t"):
        # store the dataframe and lookup delimiter
        self.df = df
        self.delim = delim

        # initialize the co-occurrence matrix
        self.coo_matrix = {
            "meta": {
                "delim": self.delim,
                "total_pills": len(self.df),
            },
            "data": {},
        }

    def compute(self, verbose=True):
        # compute all combinations of shapes, colors, and imprint characters
        # from pills in the dataframe
        all_combinations = self._get_combinations()

        # check to see if we need wrap the combinations in a progress bar
        all_combinations = tqdm(all_combinations) if verbose \
            else all_combinations

        # loop over the combinations
        for (shape, color, char) in all_combinations:
            # compute the matching conditions for the current combination
            matches_shape = self.df["Shape"] == shape
            matches_color = self.df["Colors"].str.contains(
                color,
                na=False,
                regex=False
            )
            matches_char = self.df["Imprints"].str.contains(
                char,
                na=False,
                regex=False
            )

            # grab the index values directly
            matches_shape_idx = self.df[matches_shape].index
            matches_color_idx = self.df[matches_color].index
            matches_char_idx = self.df[matches_char].index

            # compute the intersection between the indexes
            inter_idxs = matches_shape_idx.intersection(matches_color_idx)
            inter_idxs = inter_idxs.intersection(matches_char_idx)

            # construct the key to the co-occurrence matrix, then store the
            # intersection indexes in the dictionary
            key = self.delim.join([shape, color, char])
            self.coo_matrix["data"][key] = inter_idxs

        # return the co-occurrence matrix
        return self.coo_matrix

    def _get_combinations(self):
        # get all unique shapes, colors, and imprint characters from the pills
        # in the dataframe
        shapes = self.df["Shape"].unique().tolist()
        colors = self.df["Colors"].str.split().explode().unique().tolist()
        chars = self.df["Imprints"].astype(str).str.replace(" ", "")
        chars = list(set("".join(chars)))

        # compute all combinations of the shapes, colors, and characters, then
        # sort the combinations, thereby guaranteeing the same index values
        # into our co-occurrence matrix
        all_combinations = itertools.product(shapes, colors, chars)
        all_combinations = sorted(list(all_combinations))

        # return the combinations
        return all_combinations
