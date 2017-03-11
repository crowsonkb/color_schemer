# color_schemer

A web application to translate color schemes between dark- and light-background using the [CIECAM02](https://en.wikipedia.org/wiki/CIECAM02) color appearance model.

Python 3, [Flask](http://flask.pocoo.org), [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/), and special thanks to the authors of the [colour-science](http://colour-science.org) Python module.

## Running the application

When `run.sh` is invoked for the first time, it will create a Python virtual environment in `venv` and install dependencies into it. (If `venv` is later removed, it will be recreated.) The included sample uWSGI web server configuration (`uwsgi_example.ini`) will serve HTTP on port 8000 by default; for deployment, use of the `socket` or `http-socket` directives and a reverse proxy are preferred. (See the [Flask deployment guide for uWSGI](http://flask.pocoo.org/docs/0.12/deploying/uwsgi/).)
