import logging

config = {
    "settings": {
        # To be used by Flask: DEVELOPMENT ONLY
        "debug": True,

        # Flask host: DEVELOPMENT ONLY
        "host": "localhost",

        # Flask port: DEVELOPMENT ONLY
        "port": 5904,

        # Logging configurations
        "logging": {
            "level": logging.INFO,
            "format": "%(asctime)s | %(levelname)-8s | %(name)-20s | Line: %(lineno)-5d | %(message)s",
            "datefmt": "%d-%m-%Y | %H:%M:%s"
        },

        #folders
        "folders": {
            "tmp": "/tmp",
            "geoserver_datadir": "../test_data/geoserver_data_dir/",
            "distribution": "../test_data/distribution/",
            "storage": "../test_data/storage/",
            # this is used by the filesystem to get the (published) layers in the file system
            "workspace_layer_separator": ":"
        },

        # Database
        "db": {
            # Spatial Database
            "spatial": {
                # default_db will search in the dbs["database"] as default option
                "dbname": "fenix",
                "host": "localhost",
                "port": "5432",
                "username": "user",
                "password": "pwd",
                "schema": "public",
            }
        }
    }
}
#
# config = merge_config_from_file(config)
# print config
