from os import path, environ
import sqlite3
from sys import platform


class Spatialite:

    selection = None
    key_field =
    def __init__(self, db_path, table_name, library_path=None):
        self.path = db_path
        self.library_path = library_path
        self.table_name = table_name

        self.primary_field =

        if not self.library_path:
            library_path = get_default_library_path()

        # Add spatialite dynamic libraries path to environment and load them
        environ["path"] = library_path + ';' + environ['path']

        self.connection = sqlite3.connect(db_path)
        self.connection.enable_load_extension(True)
        self.connection.execute("SELECT load_extension('mod_spatialite')")


    def _set_key_field(self):
        query = "SELECT"
        self.primary_field =

    def get_bbox_by_id(self, id):
        query = f"SELECT AsGeoJSON(GEOMETRY), AsGeoJSON(Envelope(GEOMETRY)) FROM {self.table_name} where ogc_fid = {id}"
        cursor = self.connection.execute(query)


    def cursor(self):
        return self.connection.cursor()

    def execute(self, query):
        return self.connection.execute(query)

    def executemany(self, query, data):
        return self.connection.executemany(query, data)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def update_timeseries(self):
        pass

def api_update():
 pass

def ___get_default_library_path():
    """
        Returns default library path as string for each operating system.
    """
    absolute_dir = path.dirname(path.abspath(__file__))

    os_cases = {"linux": absolute_dir + "/spatialite/linux",
                "linux2": absolute_dir + "/spatialite/linux",
                "darwin": absolute_dir + "/spatialite/mac",
                "win32": absolute_dir + r"\spatialite\windows",
                "win64": absolute_dir + r"\spatialite\windows"}

    return os_cases[platform]

def __set_key_field(connection, table):
    query = "SELECT"
    primary_field =

if __name__ == "__main__":
    slite = "../dbs/samo_nesusni.sqlite"
    ds = Spatialite(slite)
