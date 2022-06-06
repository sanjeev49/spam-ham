from ast import Mod
import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

# 1,2,3,4,5
class SMSInfrence(Model):
    # uuid identify data uniquely 
    __keyspace__ = "spam_infrences"
    uuid = columns.UUID(primary_key=True, default=uuid.uuid1)
    query = columns.Text()
    label = columns.Text()
    confidence = columns.Float()
    model_version = columns.Text(default='v1')