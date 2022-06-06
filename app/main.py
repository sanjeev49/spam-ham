import pathlib
from pickle import OBJ
#from sqlite3.dbapi2 import _Statement
from typing import Optional
from unittest import result
import uuid
from attr import has
from fastapi import FastAPI 
from cassandra.cqlengine.management import sync_table
from cassandra.query import SimpleStatement
from fastapi.responses import StreamingResponse

from . import (
    config,
    db ,
    models,
    ml,
    schema 

)



app = FastAPI()

settings = config.get_settings()
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR/"models"
SMS_SPAM_DIR = MODEL_DIR/"spam-sms"
MODEL_PATH = SMS_SPAM_DIR/"spam-model.h5"
TOKENIZER_PATH = SMS_SPAM_DIR/"spam-classifer-tokenizer.json"
METADATA_PATH = SMS_SPAM_DIR/"spam-classifer-metadata.json"

SPAM_MODEL = None
DB_SESSION = None
SMSInfrence = models.SMSInfrence

@app.on_event("startup")
def on_startup():
    # load my model 
   global SPAM_MODEL, DB_SESSION
   SPAM_MODEL = ml.AIModel(
        model_path = MODEL_PATH,
        toeknizer_path = TOKENIZER_PATH,
        metadata_path = METADATA_PATH

   )
   DB_SESSION = db.get_session()
   sync_table(SMSInfrence)


@app.get("/")
def read_index(q:Optional[str] = None):
    return {"hello":"world"}

@app.post("/")
def create_inference(query:schema.Query):
    global SPAM_MODEL
    preds_dict = SPAM_MODEL.predict_text(query.q)
    top = preds_dict.get('top') # {label: , conf}
    data = {"query": query.q, **top}
    obj = SMSInfrence.objects.create(**data)
    # NoSQL -> cassandra -> DataStax AstraDB
    return obj

@app.get("/infrences")
def list_infrences():
    q = SMSInfrence.objects.all()
    return list(q)

def fetch_rows(stmt:SimpleStatement, fetch_size:int=25, session = None):
    stmt.fetch_size = fetch_size
    result_set = session.execute(stmt)
    has_pages = result_set.has_more_pages
    yield "uuid, label, confidence, query, version\n"
    while has_pages:
        for row in result_set.current_rows:
            yield f"{row['uuid']}, {row['label']}, {row['confidence']}, {row['query']}, {row['model_version']} \n"
        has_pages = result_set.has_more_pages
        result_set = session.execute(stmt, paging_state = result_set.paging_state)

@app.get("/infrencecs/{my_uuid}")
def read_infrences(my_uuid):
    obj = SMSInfrence.objects.get(uuid=my_uuid)
    return obj

@app.get("/dataset") # /?q=this is awesome
def export_inferences():
    global DB_SESSION
    cql_query = "SELECT * FROM spam_infrences.smsinfrence LIMIT 10000"
    #rows = DB_SESSION.execute(cql_query)
    statement = SimpleStatement(cql_query) 
    return StreamingResponse(fetch_rows(statement, 25, DB_SESSION))


#docker run -it spam-classifier /bin/bash