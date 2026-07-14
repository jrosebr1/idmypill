# import the necessary packages
from pathlib import Path
from enum import Enum
import json

# load the JSON dictionary that maps GSDB table names to filenames
base_dir = Path(__file__).resolve().parent
GSDB_TABLE_FILENAMES_PATH = base_dir / "data" / "gsdb_table_filenames.json"
GSDB_TABLE_FILENAMES = json.loads(open(GSDB_TABLE_FILENAMES_PATH).read())


def gsdb_table_filenames():
    # return a dictionary that maps GSDB table names to their associated
    # filenames
    return {table: GSDB_TABLE_FILENAMES[table.value] for table in GSDBTable}


class GSDBTable(Enum):
    # define the names of tables commonly used in GSDB
    DRUG_ITEMS = "drug_items"
    DRUG_ITEM_VERSIONS = "drug_item_versions"
    DRUG_IMAGES = "drug_images"
    PRODUCTS = "products"
    SHAPES = "shapes"
    COLORS = "colors"
    ROUTES = "routes"
    DEA_CLASSIFICATION = "dea_classification"


class GSDBColumn(Enum):
    # define column names related to the "drug items" table
    DRUG_ITEM_ID = "DrugItemID"
    DRUG_ITEM_DESC = "Description"
    DRUG_ITEM_VERSION = "Version"
    DRUG_ITEM_ROUTE_ID = "ImplicitRouteID"

    # define column names related to the "products" table
    PRODUCT_ID = "ProductID"
    PRODUCT_NDC = "NDC9"
    PRODUCT_NAME = "ProductNameShort"

    # define column names related to the "DEA classification" table
    DEA_ID = "DEAClassificationID"
    DEA_CLASSIFICATION = "Classification"

    # define column names related to the "color" table
    COLOR_NAME = "ColorName"

    # define column names related to the "routes" table
    ROUTE_ID = "RouteID"
    ROUTE_NAME = "RouteName"

    # define column names related to the "drug images" table
    DRUG_IMAGES_ITEM_ID = "DrugItemId"
    DRUG_IMAGES_VERSION = "Version"
    DRUG_IMAGES_ID_TYPE = "IdentifierType"
    DRUG_IMAGES_NDC = "NDC11"
    DRUG_IMAGES_FILENAME = "ImageName"
