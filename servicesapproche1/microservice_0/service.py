# Auto-generated service module

# From file: monolith/main.py
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# From file: monolith/main.py
def read_page1(request: Request):
    result = square(4)
    return templates.TemplateResponse("page1.html", {"request": request, "result": result})

# From file: monolith/main.py
def read_page2(request: Request):
    result = cube(2)
    return templates.TemplateResponse("page2.html", {"request": request, "result": result})

# From file: monolith/main.py
def read_page3(request: Request):
    result = add_five(10)+cube(2)+square(3)
    return templates.TemplateResponse("page3.html", {"request": request, "result": result})

