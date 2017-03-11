"""A web application to translate color schemes between dark- and light-background."""

from functools import partial

import flask
from werkzeug.exceptions import HTTP_STATUS_CODES, InternalServerError

import cam
from color_io import color_to_decimal, color_to_hex, parse_color

app = flask.Flask(__name__)


@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(err):
    context = dict(code=err.code, reason=HTTP_STATUS_CODES[err.code], message=err.description)
    return flask.render_template('error.html', **context), err.code


@app.route('/')
def index():
    """Renders the main UI page."""
    return flask.render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    """Renders the result page."""
    dark, light = [0.2]*3, [0.8]*3
    form = flask.request.form

    J_factor, C_factor = float(form['J_factor']), float(form['C_factor'])

    if form['direction'] == 'to_dark':
        translate_fn = partial(cam.translate, bg_src=light, bg_dst=dark)
        left_bg, right_bg = '#fff', '#000'
    elif form['direction'] == 'to_light':
        translate_fn = partial(cam.translate, bg_src=dark, bg_dst=light)
        left_bg, right_bg = '#000', '#fff'
    else:
        raise InternalServerError('Translation direction not specified.')
    translate_fn = partial(translate_fn, J_factor=J_factor, C_factor=C_factor)

    outputs = []
    for color in form['colors'].split('\n'):
        if len(outputs) == 256:
            break
        if not color.strip():
            continue
        try:
            rgb_src = parse_color(color)
        except ValueError as err:
            raise InternalServerError(str(err))
        rgb_dst = translate_fn(rgb_src)
        if color.count(','):
            outputs.append((color_to_decimal(rgb_src), color_to_decimal(rgb_dst)))
        else:
            outputs.append((color_to_hex(rgb_src), color_to_hex(rgb_dst)))

    return flask.render_template('result.html',
                                 left_bg=left_bg, right_bg=right_bg, outputs=outputs)
