"""A web application to translate color schemes between dark- and light-background."""

from functools import partial
import re

import flask

import cam

app = flask.Flask(__name__)


def parse_hex_color(color):
    """Parses a hex format color string, i.e. #ccc or #12ab34, into an (r, g, b) tuple."""
    color = color.strip('#')
    if len(color) == 3:
        color = ''.join(ch*2 for ch in color)
    if len(color) == 6:
        r = int(color[0:2], base=16) / 255
        g = int(color[2:4], base=16) / 255
        b = int(color[4:6], base=16) / 255
        return (r, g, b)
    else:
        raise ValueError('Could not parse hex format color')


def parse_color(color):
    """Parses a color string (i.e. #12ab34 or rgb(130, 12, 24)) into an (r, g, b) tuple."""
    components = color.split(',')
    if len(components) == 1:
        return parse_hex_color(color.strip())
    if len(components) != 3:
        raise ValueError('Could not parse decimal format color')
    return tuple(float(re.search(r'([\d.]+)', c).group(1)) / 255 for c in components)


def color_to_int(rgb):
    """Converts a color from floating point range 0-1 to integer range 0-255."""
    return tuple(int(round(c * 255)) for c in rgb)


def color_to_decimal(rgb):
    """Stringifies a color using the CSS RGB color format."""
    return 'rgb(%d, %d, %d)' % color_to_int(rgb)


def color_to_hex(rgb):
    """Stringifies a color using the CSS hex color format."""
    return '#%02x%02x%02x' % color_to_int(rgb)


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
    elif form['direction'] == 'to_light':
        translate_fn = partial(cam.translate, bg_src=dark, bg_dst=light)
    else:
        raise ValueError('Translation direction not specified')
    translate_fn = partial(translate_fn, J_factor=J_factor, C_factor=C_factor)

    outputs = []
    for color in form['colors'].split('\n'):
        rgb_src = parse_color(color)
        rgb_dst = translate_fn(rgb_src)
        if color.count(','):
            outputs.append((color_to_decimal(rgb_src), color_to_decimal(rgb_dst)))
        else:
            outputs.append((color_to_hex(rgb_src), color_to_hex(rgb_dst)))

    return flask.render_template('result.html', outputs=outputs)
