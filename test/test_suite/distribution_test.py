import unittest
import os
import requests
import simplejson
from geobricks_distribution.config.config import config
from geobricks_distribution.core.distribution_core import Distribution


json_request = {
    "raster": [
        {
            "workspace": "workspace",
            "layerName": "rice_area_3857",
            "datasource": "geoserver",
            "_name": "optional",
            "_path": "optional"
        },
        {
            # "uid": "fenix:rice_area1",
            "workspace": "workspace",
            "layerName": "rice_area_4326",
            "datasource": "storage",
            "_name": "optional",
            "_path": "optional"
        }
    ],
    "vector":
        {
             # Database
            "type": "database",
            "options": {
                "db": "spatial",    #optional
                "layer": "gaul0_2015_4326",   # required (table or table alias)
                "column": "adm0_name", # required (column or column_alias)
                "codes": ["Italy"]
            }
        }
}

class GeobricksTest(unittest.TestCase):

    distribution = Distribution(config)

    def test_distribution(self):
        result = self.distribution.export_raster_by_spatial_query(json_request)
        self.assertEqual(os.path.isfile(result), True)

    def test_distribution_raster_spatialquery_rest(self):
        headers = {'content-type': 'application/json'}
        data = simplejson.dumps(json_request)
        r = requests.post("http://localhost:5904/distribution/rasters/spatialquery/", data=data, headers=headers)
        self.assertIsNotNone(200, r.status_code)

    def test_distribution_download_rest(self):
        headers = {'content-type': 'application/json'}
        data = simplejson.dumps(json_request)
        r = requests.post("http://localhost:5904/distribution/rasters/spatialquery/", data=data, headers=headers)
        uid = simplejson.loads(simplejson.loads(r.text))
        r = requests.get( uid["url"])
        self.assertIsNotNone(200, r.status_code)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(GeobricksTest)
    unittest.TextTestRunner(verbosity=2).run(suite)






