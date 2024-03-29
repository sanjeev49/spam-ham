import pathlib
from . import config
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection

BASE_DIR = pathlib.Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / 'ignored'
# if not SOURCE_DIR.exists():
#     SOURCE_DIR = BASE_DIR / 'decrypted'
SOURCE_DIR = BASE_DIR/"ignored"
if not SOURCE_DIR.exists():
    SOURCE_DIR = BASE_DIR/"decrypted"
CLUSTER_BUNDLE = str( SOURCE_DIR / 'secure-connect-spam-classifier.zip')

settings = config.get_settings()

ASTRA_DB_CLIENT_ID = settings.db_client_id
ASTRA_DB_CLIENT_SECRET  = settings.db_client_secret


def get_cluster():
    cloud_config= {
        'secure_connect_bundle': CLUSTER_BUNDLE
    }
    auth_provider = PlainTextAuthProvider(ASTRA_DB_CLIENT_ID, ASTRA_DB_CLIENT_SECRET)
    return Cluster(cloud=cloud_config, auth_provider=auth_provider)
    

def get_session():
    cluster = get_cluster()
    session = cluster.connect()
    connection.register_connection(str(session), session=session)
    connection.set_default_connection(str(session))
    return session