"""A web application to translate color schemes between dark- and light-background."""

import flask

app = flask.Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'
