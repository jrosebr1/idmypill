# import the necessary packages
from collections import Counter
from .helpers import round_or_other_shapes
from .helpers import white_or_other_colors
from .helpers import preprocess_imprints
import itertools


class CoOccurrenceSearch:

    def __init__(self, rxpills, coo_matrix):
        # store the prescription pills (from our database) along with our
        # co-occurrence matrix
        self.coo_matrix = coo_matrix
        self.rxpills = rxpills

        # grab the total number of pills represented in the matrix, along
        # with the lookup delimiter, from the metadata
        metadata = coo_matrix.get("meta", {})
        self.num_pills = metadata.get("total_pills", 0)
        self.delim = metadata.get("delim", "\t")

    def search(
            self,
            query_shape,
            query_colors,
            query_imprints,
            expand_shape=True,
            expand_color=True,
            clean_imprints=True,
            coo_n=1000,
            rerank_n=100
    ):
        # if the co-occurrence matrix is empty, return an empty search
        # result list
        if not self.coo_matrix or self.num_pills == 0:
            return []

        # check to see if we'll expand the query shape, effectively treating
        # our search as round vs. non-round shapes
        query_shape = round_or_other_shapes(query_shape) \
            if expand_shape else [query_shape]

        # check to see if we'll expand the query color, thereby treating our
        # search as white vs. non-white colors
        query_colors = white_or_other_colors(query_colors) \
            if expand_color else query_colors

        # check to see if we need to clean the imprint before performing the
        # search
        query_imprints = preprocess_imprints(query_imprints) \
            if clean_imprints else query_imprints

        # perform an initial filtering using our co-occurrence matrix
        coo_scores = self._coo_filter(
            query_shape,
            query_colors,
            query_imprints,
            coo_n
        )

        # re-rank the results based on how much of an overlap there is
        # between our pill imprints and the query imprints
        results = self._rerank(coo_scores, query_imprints, rerank_n)

        # return the results
        return results

    def _coo_filter(self, query_shape, query_colors, query_imprints, n):
        # initialize a dictionary to accumulate co-occurrence scores (the
        # *larger* the accumulated value, the *more likely* a match)
        scores = Counter()

        # compute the combinations of the shape, colors, and characters on the
        # imprint
        combinations = itertools.product(
            query_shape,
            query_colors,
            [c for c in query_imprints]
        )

        # loop over the combinations
        for (shape, color, char) in combinations:
            # construct the key to the co-occurrence matrix, then grab all pill
            # indexes for that key
            key = self.delim.join([shape, color, char])
            idxs = self.coo_matrix["data"].get(key, [])

            # compute the discriminative power of our co-occurrence, where the
            # larger the value, the more powerful it is
            importance = 1.0 - (len(idxs) / self.num_pills)

            # update our scores dictionary, assigning the same importance to
            # each of the pills fetched from the index
            scores.update({i: importance for i in idxs})

        # return the top-N scores
        return scores.most_common(n)

    def _rerank(self, coo_scores, query_imprints, n):
        # initialize our list of re-ranked results
        results = Counter()

        # loop over the co-occurrence scores
        for (i, _) in coo_scores:
            # grab the pill imprint, then find the longest common string
            # between the current pill imprint and the query imprint
            pill_imprint = self.rxpills[i].concat_imprints(sep="")
            common_substring = self._find_longest_common_substring(
                pill_imprint,
                query_imprints
            )

            # our re-rank score will be the sum of the common substring
            # overlaps between the original pill imprint and the query
            # imprint
            score = sum([
                len(common_substring) / len(pill_imprint),
                len(common_substring) / len(query_imprints),
            ])

            # update the results
            results.update({i: score})

        # return the re-ranked results
        return results.most_common(n)

    @staticmethod
    def _find_longest_common_substring(long: str, short: str):
        # use a list comprehension to generate all substrings of 'short' that
        # are within 'long'
        substrings = [
            short[i:j]
            for i in range(len(short))
            for j in range(i + 1, len(short) + 1)
            if short[i:j] in long
        ]

        # find the longest common substring
        return max(substrings, key=len, default="") if substrings else ""
