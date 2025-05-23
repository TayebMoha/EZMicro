from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from timeit import default_number
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")
def square(x: int) -> int:
    return x ** 2
def cube(x: int) -> int:
    return x ** 3
default_number=1000
def add_five(x: int) -> int:
    return x + 5 + default_number
@app.get("/page3")
def read_page3(request: Request):
    result = add_five(10)+cube(2)+square(3)
    return templates.TemplateResponse("page3.html", {"request": request, "result": result})