from flask import Flask
from service import *

app = Flask(__name__)

@app.route('/')
def index():
    return 'Service: microservice_0'

if __name__ == '__main__':
    app.run(debug=True, port=8000)
