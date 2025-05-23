from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from timeit import default_number
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")
def cube(x: int) -> int:
    return x ** 3
@app.get("/page2")
def read_page2(request: Request):
    result = cube(2)
    return templates.TemplateResponse("page2.html", {"request": request, "result": result})