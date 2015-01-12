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
            "distribution": "../../test_data/distribution/",
        },

        # Database
        "db": {
            # Spatial Database
            "spatial": {
                # default_db will search in the dbs["database"] as default option
                "dbname": "db",
                "host": "localhost",
                "port": "5432",
                "username": "usr",
                "password": "pwd",
                "schema": "spatial",
            }
        }
    }
}
