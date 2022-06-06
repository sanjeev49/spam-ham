import pathlib
import json
import numpy as np 
from pickle import NONE
from typing import Optional
from fastapi import FastAPI 
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

app = FastAPI()
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR/"models"
SMS_SPAM_DIR = MODEL_DIR/"spam-sms"
MODEL_PATH = SMS_SPAM_DIR/"spam-model.h5"
TOKENIZER_PATH = SMS_SPAM_DIR/"spam-classifer-tokenizer.json"
METADATA_PATH = SMS_SPAM_DIR/"spam-classifer-metadata.json"

AI_MODEL = None
AI_TOKENIZER = None
MODEL_METADATA = {}
LEGEND_INVERTED = {}
labels_legend_inverted = {}

@app.on_event("startup")
def on_startup():
    # load my model 
    global AI_MODEL , AI_TOKENIZER, MODEL_METADATA, LEGEND_INVERTED,labels_legend_inverted
    if MODEL_PATH.exists():
        AI_MODEL = load_model(MODEL_PATH)
    else:
        print("MOdel not exists")
    if TOKENIZER_PATH.exists():
        t_json = TOKENIZER_PATH.read_text()
        AI_TOKENIZER = tokenizer_from_json(t_json)
        #print(AI_TOKENIZER)
    else:
        print("not exists")
    if METADATA_PATH.exists():
        MODEL_METADATA = json.loads(METADATA_PATH.read_text())
        labels_legend_inverted = MODEL_METADATA['labels_legend_inverted']
    else:
        print("path does not exist.")

def predict(query:str):
    # sequences, pad_sequences
    sequences = AI_TOKENIZER.texts_to_sequences([query])
    maxlen = MODEL_METADATA.get('max_sequence') or 280
    x_input = pad_sequences(sequences, maxlen = maxlen)
    #print(x_input)
    #print(x_input.shape)
    preds_array = AI_MODEL.predict(x_input) # list of predictions 
    preds = preds_array[0]
    top_idx_val  = np.argmax(preds)
    top_pred  = {
        "label":labels_legend_inverted[str(top_idx_val)], "Confidence":preds[top_idx_val]
    }
    labeled_preds = [{"label":labels_legend_inverted[str(i)], "confidence":x} for i, x in enumerate(list(preds))]
    print(labeled_preds)
    return json.loads(json.dumps({"top_prediction":top_pred, "all_predictioin":labeled_preds}, cls = NumpyEncoder))


@app.get("/")
def read_index(q:Optional[str] = None): # /?q=this is awesome
    global AI_MODEL, MODEL_METADATA, labels_legend_inverted

    query = q or "take my phone for huge discount call on 912344323"
    pred = predict(query)
    #print(AI_MODEL)
    return {"query":query, "predictoin":pred}