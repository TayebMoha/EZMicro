from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from timeit import default_number
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")
def square(x: int) -> int:
    return x ** 2
@app.get("/page1")
def read_page1(request: Request):
    result = square(4)
    return templates.TemplateResponse("page1.html", {"request": request, "result": result})