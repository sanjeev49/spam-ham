import json
from pydantic import BaseModel
from fastapi import FastAPI, Request, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



class Liste(BaseModel):
    data: str

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name = "static")
templates = Jinja2Templates(directory="templates")

@app.get('/', response_class=HTMLResponse)
def main(request:Request):
    return templates.TemplateResponse("item.html", {"request":request})

@app.post("/")
#@cross_origin()
def post_basic(inp: Liste):
    return {"text":inp.data}
    