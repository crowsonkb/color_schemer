# color_schemer

A web application to translate color schemes between dark- and light-background using the [CIECAM02](https://en.wikipedia.org/wiki/CIECAM02) color appearance model.

Python 3, [Flask](http://flask.pocoo.org), [Gunicorn](http://gunicorn.org), and special thanks to the authors of the [colour-science](http://colour-science.org) Python module.

## Running the application

When `app.sh` is invoked for the first time, it will create a Python virtual environment and install dependencies into it. (If the `venv` directory is later removed, it will be recreated.) The included sample web server configuration (`gunicorn_config_example.py`) will serve HTTP on port 8000 by default, but for deployment use of a reverse proxy such as [nginx](http://nginx.org/en/) is preferred. (See the [Flask deployment guide for Gunicorn](http://flask.pocoo.org/docs/0.12/deploying/wsgi-standalone/#gunicorn).)
