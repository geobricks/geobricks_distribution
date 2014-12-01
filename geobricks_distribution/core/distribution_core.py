import os
import json
import uuid
from shutil import move
from geobricks_distribution.config.config import config
from geobricks_distribution.utils.log import logger
from geobricks_distribution.utils.filesystem import get_raster_path_by_uid
from geobricks_distribution.utils import email_utils
from geobricks_distribution.utils.filesystem import zip_files, get_filename

# TODO: remove dependencies
from geobricks_gis_raster.core.raster import get_authority, crop_by_vector_database
from geobricks_dbms.core.dbms_postgresql import DBMSPostgreSQL

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


def export_by_spatial_query(user_json, distribution_url, distribution_folder=None):
    try:
        if distribution_folder is None:
            distribution_folder = config["settings"]["folders"]["distribution"]
        if not os.path.isdir(distribution_folder):
            os.makedirs(distribution_folder)
    except Exception, e:
        log.error(e)
        raise Exception(e)

    print config["settings"]["db"]["spatial"]

    # TODO remove dependency from here?
    db_spatial = DBMSPostgreSQL(config["settings"]["db"]["spatial"])

    # TODO check if uids or paths (or both)
    uids = user_json["raster"]["uids"]
    json_filter = json.loads(user_json["vector"])
    email_address = None if "email_address" not in user_json else user_json["email_address"]

    # create a random tmp folder
    zip_folder_id = str(uuid.uuid4()).encode("utf-8")
    zip_folder = os.path.join(distribution_folder, zip_folder_id)
    os.mkdir(zip_folder)

    # create a valid folder name to zip it
    output_folder = os.path.join(zip_folder, "layers")
    os.mkdir(output_folder)

    output_files = []
    for uid in uids:

        raster_path = get_raster_path_by_uid(uid)
        print raster_path

        authority_name, authority_code = get_authority(raster_path)
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
        #dst_file = tmp_folder

        log.info(filepath)
        log.info(dst_file)
        move(filepath, dst_file)

        # rename file based on uid layer_name (i.e. fenix:trmm_08_2014 -> trmm_08_2014)
        output_filename = uid.split("|")[1] + ".tif" if "|" in uid else uid.split(":")[1] + ".tif"
        output_file = os.path.join(output_folder, output_filename)
        os.rename(dst_file, output_file)

        # saving the output file to zip
        output_files.append(output_file)

    # zip folder or files
    # TODO: change and use make_archive
    #output_filename = os.path.join(zip_folder, zip_filename)
    #make_archive(folder_to_zip, output_filename)
    zip_files(zip_filename, output_files, zip_folder)

    # URL to the resource
    url = distribution_url + zip_folder_id

    # send email if email address
    if email_address:
        log.info("sending email to: %s" % email_address)
        html = email_body.replace("{{LINK}}", url)
        email_user = config["settings"]["email"]["user"]
        email_password = config["settings"]["email"]["password"]
        email_utils.send_email(email_user, email_address, email_password, email_header, html)

    return '{ "url" : "' + url + '"}'