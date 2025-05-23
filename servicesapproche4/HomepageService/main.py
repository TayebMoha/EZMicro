from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from timeit import default_number
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})