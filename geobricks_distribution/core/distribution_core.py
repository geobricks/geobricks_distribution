import os
import json
import uuid
from shutil import move
from geobricks_common.core.log import logger
from geobricks_common.core.filesystem import get_raster_path, zip_files, get_filename
from geobricks_common.core.email_utils import send_email


# TODO: remove dependencies
from geobricks_gis_raster.core.raster import get_authority, get_srid, crop_raster_on_vector_bbox_and_postgis_db
from geobricks_spatial_query.core.spatial_query_core import SpatialQuery

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

    def export_raster_by_spatial_query(self, user_json, distribution_url=None, distribution_folder=None):
        print user_json
        print self.config
        try:
            if distribution_folder is None:
                # turning relative to absolute path if required
                if not os.path.isabs(self.config["settings"]["folders"]["distribution"]):
                    self.config["settings"]["folders"]["distribution"] = os.path.abspath(self.config["settings"]["folders"]["distribution"])
                distribution_folder = self.config["settings"]["folders"]["distribution"]
            if not os.path.isdir(distribution_folder):
                os.makedirs(distribution_folder)
        except Exception, e:
            log.error(e)
            raise Exception(e)

        # TODO remove dependency from here?
        sq = SpatialQuery(self.config)

        vector_filter = user_json["vector"]
        email_address = None if "email_address" not in user_json else user_json["email_address"]
        rasters = user_json["raster"]


        # create a random tmp folder
        zip_folder_id = str(uuid.uuid4()).encode("utf-8")
        zip_folder = os.path.join(distribution_folder, zip_folder_id)
        os.mkdir(zip_folder)

        # create a valid folder name to zip it
        output_folder = os.path.join(zip_folder, "layers")
        os.mkdir(output_folder)

        output_files = []
        for raster in rasters:
            raster_path = get_raster_path(raster)
            # turning relative to absolute path if required
            if not os.path.isabs(raster_path):
                raster_path = os.path.abspath(raster_path)
            log.info(raster_path)
            srid = get_srid(raster_path)
            log.info(srid)

            # retrieving bounding box
            db_options = vector_filter["options"]
            db_datasource = db_options["db"]
            layer_code = db_options["layer"]
            column_code = db_options["column"]
            codes = db_options["codes"]
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
            if email_address:
                log.info("sending email to: %s" % email_address)
                html = email_body.replace("{{LINK}}", url)
                # TODO: handle exception
                email_user = self.config["settings"]["email"]["user"]
                email_password = self.config["settings"]["email"]["password"]
                send_email(email_user, email_address, email_password, email_header, html)

            return '{ "url" : "' + url + '"}'



    def export_raster_by_spatial_query_old(self, user_json, distribution_url=None, distribution_folder=None):
        try:
            if distribution_folder is None:
                distribution_folder = self.config["settings"]["folders"]["distribution"]
            if not os.path.isdir(distribution_folder):
                os.makedirs(distribution_folder)
        except Exception, e:
            log.error(e)
            raise Exception(e)

        # TODO remove dependency from here?
        sq = SpatialQuery(self.config)
        db_spatial = sq.get_db_instance()

        # json passed by the user
        json_filter = user_json["vector"]
        email_address = None if "email_address" not in user_json else user_json["email_address"]

        # create a random tmp folder
        zip_folder_id = str(uuid.uuid4()).encode("utf-8")
        zip_folder = os.path.join(distribution_folder, zip_folder_id)
        os.mkdir(zip_folder)

        # create a valid folder name to zip it
        output_folder = os.path.join(zip_folder, "layers")
        os.mkdir(output_folder)

        output_files = []
        # gets all the raster paths
        log.info(user_json["raster"])
        # raster_paths = get_raster_paths(user_json["raster"])
        # raster_paths = get_raster_path(user_json["raster"])
        # log.info(raster_paths)
        for raster_path in user_json["raster"]:
            log.info(raster_path)
            authority_name, authority_code = get_authority(raster_path).upper().split(":")
            log.info(authority_name, authority_code)
            log.info(db_spatial.schema)
            log.info(authority_name)
            log.info(authority_code)

            query_extent = json_filter["query_extent"]
            query_layer = json_filter["query_layer"]

            query_extent = query_extent.replace("{{SCHEMA}}", db_spatial.schema)
            query_extent = query_extent.replace("{{SRID}}", authority_code)
            query_layer = query_layer.replace("{{SCHEMA}}", db_spatial.schema)

            # create the file on tm folder
            filepath = crop_by_vector_database(raster_path, db_spatial, query_extent, query_layer)

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
        if None:
            return zip_path
        else:
            url = distribution_url + zip_folder_id

            # send email if email address
            if email_address:
                log.info("sending email to: %s" % email_address)
                html = email_body.replace("{{LINK}}", url)
                # TODO: handle exception
                email_user = self.config["settings"]["email"]["user"]
                email_password = self.config["settings"]["email"]["password"]
                send_email(email_user, email_address, email_password, email_header, html)

            return '{ "url" : "' + url + '"}'


# gets all the rasters paths in the filesystem
# def get_raster_paths(data):
#     paths = []
#     if "uids" in data:
#         for uid in data["uids"]:
#             log.info(uid)
#             paths.append(get_raster_path({"uid": uid}))
#     if "ftp_uids" in data:
#         for uid in data["ftp_uids"]:
#             paths.append(get_raster_path({"uid": uid}))
#     if "paths" in data:
#         for path in data["paths"]:
#             paths.append(path)
#     return paths