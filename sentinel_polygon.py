
from sentinelhub import WmsRequest, BBox, CRS, MimeType, CustomUrlParam
from s2cloudless import S2PixelCloudDetector, CloudMaskRequest
from PIL import Image, ImageDraw

import pyproj
from shapely.geometry import shape
from shapely.ops import transform
from functools import partial

import json

class ApiKeyException(Exception):
    pass 

def read_api_key():
    try:
        with open("./assets/api.id", "r") as file:
            return file.read().strip()
    except:
        raise Exception(">>api.id<< file not found in assets folder. Provide said file with sentinel hub api key or change"\
              "variable to your api key string in get_all_bands function request. This requires changing layer"\
              "variable in main.py function update_for_category to layer configured on your sentinel-hub configuration manager.")


bands = {"B01": 0, "B02": 1, "B03": 2, "B04": 3, "B05": 4, "B08": 5, "B8A": 6, "B09": 7, "B10": 8, "B11": 9, "B12": 10}


class SentinelHubInterface:
    def __init__(self, api_key):
        self.api_key = api_key
    
    @classmethod
    def parse_bbox(geojson):
        bbox = self.geom_wgs.bbox
        minx, miny = bbox[0][0] #bbox[0:2]
        maxx, maxy = bbox[0][2] #bbox[4:6]



    def get_all_bands(geojson):
        pass


class EOPolygon:
    def __init__(self, polygon_geojson, epsg):
        self.__geo_interface__ = json.loads(polygon_geojson)
        self.geom = shape(self.__geo_interface__)
        self.source_epsg = epsg.lower()

        project = partial(
            pyproj.transform,
            pyproj.Proj(init=epsg),  # source coordinate system
            pyproj.Proj(init='epsg:4326'))  # destination coordinate system

        self.geom_wgs = transform(project, self.geom)


    def get_all_bands(self, wms_layer_name):
        

        #bounding_box = BBox([top, left, bot, right], crs=CRS.WGS84)
        #lat, lon = top-bot, right-left
        height, width = round(maxy-miny), round(maxx-minx)

        bands_script = "return [B01,B02,B03,B04,B05,B08,B8A,B09,B10,B11,B12]"
        wms_bands_request = WmsRequest(layer=layer,
                                       custom_url_params={
                                           CustomUrlParam.EVALSCRIPT: bands_script,
                                           CustomUrlParam.ATMFILTER: 'NONE'
                                       },
                                       bbox=bounding_box,
                                       time=('2017-01-01', '2018-12-01'),
                                       width=width, height=height,
                                       image_format=MimeType.TIFF_d32f,
                                       instance_id=api_key)

        all_cloud_masks = CloudMaskRequest(ogc_request=wms_bands_request, threshold=0.1)

        masks = []
        wms_bands = []
        for idx, [prob, mask, data] in enumerate(all_cloud_masks):
            masks.append(mask)
            wms_bands.append(data)

        return wms_bands, masks, wms_bands_request.get_dates()


def extract_evi(timef_bands):
    """
    timef_bands  = numpy array [w, h, 10]
    bands_script = "return [B01,B02,B03,B04,B05,B08,B8A,B09,B10,B11,B12]"
    """
    b08 = timef_bands[:, :, 5] # nir
    b04 = timef_bands[:, :, 3] # red
    b02 = timef_bands[:, :, 1] # blue

    # constants
    L = 1
    C1 = 6
    C2 = 7.5
    G = 2.5

    return G * ((b08-b04)/(b08 + C1 * b04 - C2 * b02 + L))


def extract_evi2(timef_bands):
    """
    timef_bands  = numpy array [w, h, 10]
    bands_script = "return [B01,B02,B03,B04,B05,B08,B8A,B09,B10,B11,B12]"
    """
    b08 = timef_bands[:, :, 5] # nir
    b04 = timef_bands[:, :, 3] # red

    # constants

    return 2.5 * ((b08-b04)/(b08 + 2.5 * b04 + 1))


def extract_ndvi(timef_bands):
    """
    timef_bands  = numpy array [w, h, 10]
    bands_script = "return [B01,B02,B03,B04,B05,B08,B8A,B09,B10,B11,B12]"
    """
    b08 = timef_bands[:, :, 5]
    b04 = timef_bands[:, :, 3]

    return (b08-b04)/(b08+b04)


def to_raster(polygon, bbox):
    left, top = bbox[0][-2]
    right, bot = bbox[0][1]

    whole_poly = []
    for part in polygon[0]:
        whole_poly.append([ (round(y-left), abs(round(x-top)) ) for y, x in part])

    width = round(right-left)
    height = round(top-bot)

    img = Image.new("L", [width, height], 0)
    for part in whole_poly:
        ImageDraw.Draw(img).polygon(part, outline=1, fill=1)

    mask = np.array(img)
    return mask


def get_sentinel_data_procedure(conn, poly_id, layer):

    polygon, bbox = api_poly_bbox(conn, poly_id)

    all_bands_12, all_cloud_masks, dates = get_all_bands(bbox, layer)

    ndvi_r = [extract_ndvi(epoch) for epoch in all_bands_12]

    evi_r = [extract_evi(epoch) for epoch in all_bands_12]
    evi2_r = [extract_evi2(epoch) for epoch in all_bands_12]
    poly_mask = to_raster(polygon, bbox)

    return all_cloud_masks, ndvi_r, evi_r, evi2_r, poly_mask, dates


if __name__ == "__main__":
    from slite_api import *
    from graphs import *

    working_dir = os.path.dirname(os.path.abspath(__file__))

    test_geojson = """{"type":"FeatureCollection","name":"fields_3794","crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:EPSG::3794"}},"features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[451829.246104218473192,125898.347090572948218],[451641.608538329426665,125593.820549212046899],[451583.164050593448337,125436.943240026128478],[452256.81367239181418,125058.592082577728434],[452416.767007248068694,125406.182983323000371],[452262.965723732486367,125504.615804772998672],[452419.843032918404788,125599.972600552675431],[452136.848671249637846,125735.317730046401266],[451986.123413404391613,125796.838243452642928],[451893.842643295007292,125849.130679847949068],[451893.842643295007292,125849.130679847949068],[451829.246104218473192,125898.347090572948218]]]}}]}"""

    #testing
    #conn = sqliteConnector(r".\\dbs\raba_2018.sqlite")
    #poly_id = 123
    #layer = "ALL-BANDS"

    #all_clouds_masks, ndvis, poly_mask, dates = get_sentinel_data_procedure(conn, poly_id, layer)

    #print()