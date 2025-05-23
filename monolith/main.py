from timeit import default_number

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount static files (CSS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Template rendering setup
templates = Jinja2Templates(directory="templates")

# Math functions
def square(x: int) -> int:
    return x ** 2

def cube(x: int) -> int:
    return x ** 3

def add_five(x: int) -> int:
    return x + 5 + default_number

default_number=1000

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/page1")
def read_page1(request: Request):
    result = square(4)
    return templates.TemplateResponse("page1.html", {"request": request, "result": result})

@app.get("/page2")
def read_page2(request: Request):
    result = cube(2)
    return templates.TemplateResponse("page2.html", {"request": request, "result": result})

@app.get("/page3")
def read_page3(request: Request):
    result = add_five(10)+cube(2)+square(3)
    return templates.TemplateResponse("page3.html", {"request": request, "result": result})
