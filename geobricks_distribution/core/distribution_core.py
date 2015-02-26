import os
import json
import uuid
from shutil import move
import glob
from geobricks_common.core.log import logger
from geobricks_common.core.filesystem import get_raster_path, zip_files, get_filename, get_vector_path, make_archive, create_tmp_filename
from geobricks_common.core.email_utils import send_email


# TODO: remove dependencies
from geobricks_gis_raster.core.raster import get_authority, get_srid as get_srid_raster, crop_raster_on_vector_bbox_and_postgis_db
from geobricks_spatial_query.core.spatial_query_core import SpatialQuery
from geobricks_gis_vector.core.vector import crop_vector_on_vector_bbox_and_postgis, get_srid as get_srid_vector

log = logger(__file__)

# TODO: remove it all from here
zip_filename = "layers"
email_header = "Raster layers"
email_body = "<html><head></head>" \
             "<body>" \
             "<div><b>PGeo - Distribution Service</b></div>" \
             "<div style='padding-top:10px;'>The layers you asked to download are available at the following link:</div>" \
             "<div style='padding-top:10px;'><a href='{{LINK}}'>Download Zip File</a></div>" \
             "<div style='padding-top:10px;'><b>Please note that the link will work for the next 24h hours</b></div>" \
             "</body>" \
             "</html>"


class Distribution():

    config = None
    db_default = "spatial"

    def __init__(self, config):
        self.config = config

    def _get_distribution_folder(self, distribution_folder=None):
        try:
            if distribution_folder is None:
                # turning relative to absolute path if required
                if not os.path.isabs(self.config["settings"]["folders"]["distribution"]):
                    # raster_path = os.path.normpath(os.path.join(os.path.dirname(__file__), self.config["settings"]["folders"]["distribution"]))
                    # TODO ABS PATH
                    self.config["settings"]["folders"]["distribution"] = os.path.abspath(self.config["settings"]["folders"]["distribution"])
                distribution_folder = self.config["settings"]["folders"]["distribution"]
            if not os.path.isdir(distribution_folder):
                os.makedirs(distribution_folder)
        except Exception, e:
            log.error(e)
            raise Exception(e)
        return distribution_folder

    def export_raster_by_spatial_query(self, user_json, distribution_url=None, distribution_folder=None):
        log.info(user_json)
        log.info(self.config)

        # getting distribution folder
        distribution_folder = self._get_distribution_folder(distribution_folder)

        # TODO remove dependency from here?
        sq = SpatialQuery(self.config)

        vector_filter = user_json["extract_by"]
        db_options = vector_filter["options"]
        db_datasource = db_options["db"]
        layer_code = db_options["layer"]
        column_code = db_options["column"]
        codes = db_options["codes"]
        email_address = None if "email_address" not in user_json else user_json["email_address"]
        rasters = user_json["raster"]

        log.info(rasters)

        # create a random tmp folder
        zip_folder_id = str(uuid.uuid4()).encode("utf-8")
        zip_folder = os.path.join(distribution_folder, zip_folder_id)
        os.mkdir(zip_folder)

        # create a valid folder name to zip it
        output_folder = os.path.join(zip_folder, "layers")
        os.mkdir(output_folder)

        output_files = []
        for raster in rasters:
            log.info(raster)
            raster_path = get_raster_path(raster)
            log.info(raster_path)
            # turning relative to absolute path if required
            # TODO: handle somehow better (it is used just for test)
            if not os.path.isabs(raster_path):
                # this is used to normalize relative path used during test
                raster_path = os.path.normpath(os.path.join(os.path.dirname(__file__), raster_path))
                log.info(raster_path)
                raster_path = os.path.abspath(raster_path)
            log.info(raster_path)
            srid = get_srid_raster(raster_path)
            log.info(srid)

            # retrieving bounding box
            bbox = sq.query_bbox(db_datasource, layer_code, column_code, codes, srid)
            log.info(bbox)

            # create the file on tm folder
            db = sq.get_db_instance()
            db_connection_string = db.get_connection_string(True)
            query = sq.get_query_string_select_all(db_datasource, layer_code, column_code, codes, "*")
            log.info(query)
            filepath = crop_raster_on_vector_bbox_and_postgis_db(raster_path, db_connection_string, query, bbox[0][0], bbox[0][1], bbox[1][0], bbox[1][1])
            # bounding_box = crop_raster_with_bounding_box(raster_path, bbox[0][0], bbox[0][1], bbox[1][0], bbox[1][1])

            # move file to distribution tmp folder
            path, filename, name = get_filename(filepath, True)
            dst_file = os.path.join(output_folder, filename)
            move(filepath, dst_file)

            # rename file based on uid layer_name (i.e. fenix:trmm_08_2014 -> trmm_08_2014)
            output_filename = get_filename(raster_path) + ".tif"
            output_file = os.path.join(output_folder, output_filename)
            os.rename(dst_file, output_file)

            # saving the output file to zip
            output_files.append(output_file)

        # zip folder or files
        # TODO: change and use make_archive
        #output_filename = os.path.join(zip_folder, zip_filename)
        #make_archive(folder_to_zip, output_filename)
        zip_path = zip_files(zip_filename, output_files, zip_folder)

        # URL to the resource
        if distribution_url is None:
            return zip_path
        else:
            url = distribution_url + zip_folder_id

            # send email if email address
            self._send_email(url, email_address)

            return '{ "url" : "' + url + '"}'


    def export_vector_by_spatial_query(self, user_json, distribution_url=None, distribution_folder=None):

        vector_filter = user_json["extract_by"]
        db_options = vector_filter["options"]
        db_datasource = db_options["db"]
        layer_code = db_options["layer"]
        column_code = db_options["column"]
        codes = db_options["codes"]
        email_address = None if "email_address" not in user_json else user_json["email_address"]
        vectors = user_json["vector"]


        # getting distribution folder
        distribution_folder = self._get_distribution_folder(distribution_folder)

        # TODO remove dependency from here?
        sq = SpatialQuery(self.config)

        # get file to extract
        output_dirs = []
        for vector in vectors:
            vector_path = get_vector_path(vector)
            srid = get_srid_vector(vector_path)
            log.info(srid)

            # get query
            query = sq.get_query_string_select_all(db_datasource, layer_code, column_code, codes, "ST_Transform(geom, " + srid + ")")
            log.info(query)

            db = sq.get_db_instance()
            db_connection_string = db.get_connection_string(True)
            output_name = get_filename(vector_path)
            output_file_path = crop_vector_on_vector_bbox_and_postgis(vector_path, '"' + db_connection_string + '"', query, output_name)

            # check if filepath exists
            if output_file_path:
                output_dirs.append(os.path.dirname(output_file_path))

        # create a random tmp folder
        zip_folder_id = str(uuid.uuid4()).encode("utf-8")
        zip_folder = os.path.join(distribution_folder, zip_folder_id)
        os.mkdir(zip_folder)

        # create a valid folder name to zip it
        output_folder = os.path.join(zip_folder, "layers")
        os.mkdir(output_folder)

        # move output dirs to distribution folder
        for output_dir in output_dirs:
            for file in glob.glob(os.path.join(output_dir, "*")):
                move(file, output_folder)

        # zip the folder
        tmp_file = create_tmp_filename()
        tmp_zip_path = make_archive(zip_folder, tmp_file)
        # TODO: workaround, strangly it cannot be created a zip file in the folder to zip
        zip_path = os.path.join(zip_folder, "layers.zip")
        os.rename(tmp_zip_path, zip_path)
        log.info(zip_path)

        # URL to the resource
        if distribution_url is None:
            return zip_path
        else:
            url = distribution_url + zip_folder_id

            # send email if email address
            self._send_email(url, email_address)

            return '{ "url" : "' + url + '"}'

    def _send_email(self, url, email_address=None):
        if email_address:
            log.info("sending email to: %s" % email_address)
            html = email_body.replace("{{LINK}}", url)
            # TODO: handle exception
            email_user = self.config["settings"]["email"]["user"]
            email_password = self.config["settings"]["email"]["password"]
            send_email(email_user, email_address, email_password, email_header, html)