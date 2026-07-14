# import the necessary packages
from pathlib import Path
from pydantic import ValidationError
from .schemas import DrugProductInformation
from .schemas import DrugVersion
from .parsers import PillAppearanceParser
from .tables import GSDBTable
from .tables import GSDBColumn
from .tables import gsdb_table_filenames
import pandas as pd


class GSDBLoader:

    def __init__(self, gsdb_base_path, image_base_path, sep="|"):
        # load the GSDB table dataframes from disk
        self.tables = self._load_gsdb_tables(gsdb_base_path, sep)

        # grab the dataframe of all oral drugs in GSDB, then create an iterator
        # for it
        self.df_oral_drugs = self._get_oral_drugs_df()
        self.iter_oral_drugs = self.df_oral_drugs.iterrows()

        # store the base images path, then grab all image paths from the input
        # directory
        self.image_base_path = Path(image_base_path)
        self.all_image_paths = self._get_all_drug_image_paths_on_disk()

        # compute the set of valid pill color names, then instantiate our
        # pill appearance parser
        self.pill_appearance_parser = PillAppearanceParser(
            self._get_valid_color_names()
        )

    def __iter__(self):
        # return the iterator object itself
        return self

    def __next__(self):
        # keep looping until we've reached our stopping criteria
        while True:
            # attempt to grab the next row
            try:
                # grab the next row
                (_, row) = next(self.iter_oral_drugs)

                # parse the drug product information along with all drug
                # versions
                product_info = self._get_drug_product_info(
                    row[GSDBColumn.PRODUCT_ID.value]
                )
                drug_versions = self._get_drug_item_versions(
                    row[GSDBColumn.DRUG_ITEM_ID.value]
                )

            # we've reached stopping criteria
            except StopIteration:
                raise

            # the product information could not be parsed for this drug so
            # skip it
            except ValidationError:
                # set the product info and drug versions as empty
                product_info = None
                drug_versions = None

            # return a 2-tuple of the product information and drug versions
            return product_info, drug_versions

    def total_drugs(self):
        # return the number of rows in the dataframe we'll be examining
        return len(self.df_oral_drugs)

    @staticmethod
    def _load_gsdb_tables(gsdb_base_path, sep):
        # initialize our dictionary of loaded GSDB tables
        tables = {}

        # loop over the table name and filenames
        for (table_name, table_filename) in gsdb_table_filenames().items():
            # load the data file from disk, remove any unnamed columns, and
            # store the dataframe in our tables dictionary
            df = pd.read_csv(Path(gsdb_base_path) / table_filename, sep=sep)
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            tables[table_name] = df

        # return the dictionary of tables
        return tables

    def _get_drug_item_versions(self, drug_id):
        # initialize the list of drug versions
        drug_versions = []

        # filter the drug item versions dataframe to give us only the versions
        # of the drug for the supplied ID
        df_drug_items = self.tables[GSDBTable.DRUG_ITEM_VERSIONS]
        df_drug_items = df_drug_items[
            df_drug_items[GSDBColumn.DRUG_ITEM_ID.value] == drug_id
        ]

        # loop over all versions of the drug
        for (_, row) in df_drug_items.iterrows():
            # attempt to parse the pill appearance into shape, colors, and
            # imprints
            try:
                # parse the pill description
                pill_appearance = self.pill_appearance_parser.parse(
                    row[GSDBColumn.DRUG_ITEM_DESC.value]
                )

                # grab the drug version, attempt to derive the path to the pill
                # image, and then grab its filename
                drug_version = row[GSDBColumn.DRUG_ITEM_VERSION.value]
                image_path = self._get_drug_image_path(drug_id, drug_version)
                image_filename = image_path.name if image_path else None

                # create the drug version, then update our list
                drug_version = DrugVersion(
                    drug_id=drug_id,
                    version=drug_version,
                    pill_appearance=pill_appearance,
                    image_filename=image_filename
                )
                drug_versions.append(drug_version)

            # the pill appearance could not be successfully parsed
            except ValidationError:
                pass

        # return the drug versions
        return drug_versions

    def _get_drug_product_info(self, product_id):
        # filter the products dataframe to give us drug information for the
        # supplied product ID
        df_products = self.tables[GSDBTable.PRODUCTS]
        df_products = df_products[
            df_products[GSDBColumn.PRODUCT_ID.value] == product_id
        ]

        # ensure at least one product was found
        if len(df_products) > 0:
            # extract the product, then grab the DEA classification
            product = df_products.iloc[0]
            dea_classification = self._get_dea_classification(
                product[GSDBColumn.DEA_ID.value]
            )
            # return the drug product information (this will throw an exception
            # if either the NDC, name, or DEA classification contain an invalid
            # value)
            return DrugProductInformation(
                ndc=product[GSDBColumn.PRODUCT_NDC.value],
                name=product[GSDBColumn.PRODUCT_NAME.value],
                dea_classification=dea_classification
            )

        # no drug product information could be found for the supplied product
        return None

    def _get_dea_classification(self, dea_id):
        # filter the DEA classification dataframe on the supplied ID
        df_dea = self.tables[GSDBTable.DEA_CLASSIFICATION]
        df_dea = df_dea[df_dea[GSDBColumn.DEA_ID.value] == dea_id]

        # check to see if the DEA classification was found
        if len(df_dea) > 0:
            # grab the DEA classification value
            dea_classification = df_dea[
                GSDBColumn.DEA_CLASSIFICATION.value
            ].iloc[0]

            # determine if the value is valid (if the DEA classification is
            # NaN, then we can simply check if is a floating point type)
            is_valid = all([
                dea_classification is not None,
                type(dea_classification) != float
            ])

            # if the DEA classification is indeed valid, return it
            if is_valid:
                return dea_classification

        # otherwise, the DEA classification is either (1) invalid or (2) could
        # not be found in the database
        return None

    def _get_valid_color_names(self):
        # grab the color names from the dataframe
        df_colors = self.tables[GSDBTable.COLORS]
        color_names = df_colors[GSDBColumn.COLOR_NAME.value].str.lower()

        # build the set of valid colors
        valid_colors = {
            c for sub_colors in color_names for c in sub_colors.split("-")
        }

        # return the set of valid colors
        return valid_colors

    def _get_oral_drugs_df(self):
        # filter the drugs dataframe to give us only the oral dosage pills
        df_drugs = self.tables[GSDBTable.DRUG_ITEMS]
        implicit_route_id = GSDBColumn.DRUG_ITEM_ROUTE_ID.value
        df_drugs = df_drugs[
            df_drugs[implicit_route_id] == self._get_oral_route_id()
        ]

        # return the filtered drugs dataframe
        return df_drugs

    def _get_oral_route_id(self, key="oral"):
        # filter the route of administration to find the ID of the 'oral' route
        df_routes = self.tables[GSDBTable.ROUTES]
        df_routes = df_routes[
            df_routes[GSDBColumn.ROUTE_NAME.value].str.lower() == key.lower()
        ]

        # check to see if the route was found
        if len(df_routes) > 0:
            # return the oral route ID
            return df_routes[GSDBColumn.ROUTE_ID.value].iloc[0]

        # otherwise, the oral route ID could not be found
        return None

    def _get_drug_image_path(
            self,
            drug_id,
            version,
            ndc=GSDBColumn.DRUG_IMAGES_NDC.value
    ):
        # filter the drug images on drug item ID and version, indicating that
        # we want the row for the NDC
        df_images = self.tables[GSDBTable.DRUG_IMAGES]
        df_images = df_images[
            (df_images[GSDBColumn.DRUG_IMAGES_ITEM_ID.value] == drug_id) &
            (df_images[GSDBColumn.DRUG_IMAGES_VERSION.value] == version) &
            (df_images[GSDBColumn.DRUG_IMAGES_ID_TYPE.value] == ndc)
        ]

        # check to see if an image was found
        if len(df_images) > 0:
            # grab the name of the image filename, then build the path to the
            # image on disk
            filename = df_images[GSDBColumn.DRUG_IMAGES_FILENAME.value].iloc[0]
            image_path = Path(self.image_base_path) / filename

            # ensure the image path is valid
            if image_path in self.all_image_paths:
                # return the image path
                return image_path

        # otherwise, either (1) a pill image does not exist for the combination
        # of drug item ID, version, and NDC, *or* (2) the combination exists
        # but the image isn't actually on disk
        return None

    def _get_all_drug_image_paths_on_disk(self, ext=".JPG"):
        # return all image paths in our input directory
        return {f for f in self.image_base_path.glob("*{}".format(ext))}
