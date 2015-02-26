import unittest
import os
import requests
import simplejson
from geobricks_common.core.log import logger
from geobricks_distribution.config.config import config
from geobricks_distribution.core.distribution_core import Distribution

log = logger(__file__)

#### N.B. to run all the tests, run the distribution_main.py SERVICE


json_request_export_raster = {
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
    "extract_by": {
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


json_request_export_vector = {
    "vector": [
        {
            "layerName": "gaul1_italy_malta_4326",
            "datasource": "storage",
        },
        {
            "layerName": "gaul0_malta_4326",
            "datasource": "storage",
            }
    ],
    "extract_by": {
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


json_request_export_vector_different_prj = {
    "vector": [
        {
            "layerName": "gaul1_italy_malta_4326",
            "datasource": "storage",
            },
        {
            "layerName": "gaul0_malta_4326",
            "datasource": "storage",
            }
    ],
    "extract_by": {
        # Database
        "type": "database",
        "options": {
            "db": "spatial",    #optional
            "layer": "gaul0_faostat_3857",   # required (table or table alias)
            "column": "areanamee", # required (column or column_alias)
            "codes": ["Italy"]
        }
    }
}

class GeobricksTest(unittest.TestCase):

    distribution = Distribution(config)

    # Raster
    # def test_distribution_raster(self):
    #     result = self.distribution.export_raster_by_spatial_query(json_request_export_raster)
    #     self.assertEqual(os.path.isfile(result), True)


    # def test_distribution_raster_spatialquery_rest(self):
    #     try:
    #         requests.get("http://localhost:5904/distribution/discovery")
    #     except Exception:
    #         log.warn("Service is down. Please run rest/distribution_main.py to run the test")
    #     headers = {'content-type': 'application/json'}
    #     data = simplejson.dumps(json_request_export_raster)
    #     r = requests.post("http://localhost:5904/distribution/raster/spatialquery/", data=data, headers=headers)
    #     self.assertEqual(200, r.status_code)
    #
    # def test_distribution_download_rest(self):
    #     try:
    #         requests.get("http://localhost:5904/distribution/discovery")
    #     except Exception, e:
    #         log.warn("Service is down. Please run rest/distribution_main.py to run the test")
    #
    #     headers = {'content-type': 'application/json'}
    #     data = simplejson.dumps(json_request_export_raster)
    #     r = requests.post("http://localhost:5904/distribution/raster/spatialquery/", data=data, headers=headers)
    #     uid = simplejson.loads(simplejson.loads(r.text))
    #     r = requests.get(uid["url"])
    #     self.assertEqual(200, r.status_code)


    # Vector
    def test_distribution_vector(self):
        result = self.distribution.export_vector_by_spatial_query(json_request_export_vector)
        self.assertEqual(os.path.isfile(result), True)

    def test_distribution_vector_different_prj(self):
        result = self.distribution.export_vector_by_spatial_query(json_request_export_vector_different_prj)
        self.assertEqual(os.path.isfile(result), True)



def run_test():
    suite = unittest.TestLoader().loadTestsFromTestCase(GeobricksTest)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    run_test()






