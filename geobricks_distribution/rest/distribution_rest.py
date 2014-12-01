import json
import os
from flask import Blueprint
from flask import Response
from flask import request
from flask.ext.cors import cross_origin
from geobricks_distribution.utils.log import logger
from geobricks_distribution.core import distribution_core
from geobricks_distribution.config.config import config
from flask import request, send_from_directory

log = logger(__file__)

app = Blueprint("distribution", "distribution")

# TODO: How to map it to the download distribution URL? Get the one in the @app.route "/download/"
#distribution_url = request.host_url + "distribution/download/"

zip_filename = "layers"

@app.route('/discovery/')
@app.route('/discovery')
@cross_origin(origins='*')
def discovery():
    """
    Discovery service available for all Geobricks libraries that describes the plug-in.
    @return: Dictionary containing information about the service.
    """
    out = {
        'name': 'Distribution service',
        'description': 'Functionalities to distribute geospatial data.',
        'type': 'DISTRIBUTION'
    }
    return Response(json.dumps(out), content_type='application/json; charset=utf-8')


@app.route('/rasters/spatial_query/', methods=['POST'])
@app.route('/rasters/spatial_query', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_rasters_spatial_query():
    try:
        user_json = request.get_json()
        distribution_url = request.host_url + "distribution/download/"
        distribution_folder = config["settings"]["folders"]["distribution"]
        result = distribution_core.export_by_spatial_query(user_json, distribution_url, distribution_folder)
        return Response(json.dumps(result), content_type='application/json; charset=utf-8')
    except Exception, e:
        raise Exception(e)


@app.route('/download/<id>/', methods=['GET'])
@app.route('/download/<id>', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_zip_file(id):
    try:
        distribution_folder = config["settings"]["folders"]["distribution"]
        path = os.path.join(distribution_folder, str(id))
        return send_from_directory(directory=path, filename=zip_filename + ".zip",  as_attachment=True, attachment_filename=zip_filename)
    except Exception, e:
        log.error(e)
        raise Exception(e)