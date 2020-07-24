from pyproj import Proj, transform
from sentinelhub import BBox, CRS
from shapely.geometry import shape, GeometryCollection
import json


def load_json_as_shapely_collection(path, fix_overlaping=False):
    with open(path) as f:
        features = json.load(f)["features"]

    print()
    # buffer(0) is a trick for fixing scenarios where polygons have overlapping coordinates
    case = {
        True: lambda: [shape(feature["geometry"]).buffer(0) for feature in features],
        False: lambda: [shape(feature["geometry"]) for feature in features],
    }
    return GeometryCollection(case[fix_overlaping]())


def project_bbox_by_wgs_epsg(bbox, srs, print_epsg):
    minx, miny = bbox[0][0]
    maxx, maxy = bbox[0][2]  # bbox[4:6]

    right, bot = transform(Proj(init=srs), Proj(init='epsg:4326'), maxx, miny)
    left, top = transform(Proj(init=srs), Proj(init='epsg:4326'), minx, maxy)

    return BBox([top, left, bot, right], crs=CRS.WGS84)


if __name__ == "__main__":

    path = "tests/data/landuse_central_slovenija.geojson"
    gc = load_json_as_shapely_collection(path, True)
    print()