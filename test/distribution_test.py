import unittest
import os
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
                "layer": "gaul0_3857",   # required (table or table alias)
                "column": "adm0_name", # required (column or column_alias)
                "codes": ["China"]
            }
        }
}

class GeobricksTest(unittest.TestCase):

    distribution = Distribution(config)

    def test_distribution_geoserver(self):
        result = self.distribution.export_raster_by_spatial_query(json_request)
        self.assertEqual(os.path.isfile(result), True)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(GeobricksTest)
    unittest.TextTestRunner(verbosity=2).run(suite)






