"""A web application to translate color schemes between dark- and light-background."""

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
    rgb_src = parse_color(flask.request.form['color'])
    rgb_dst = cam.translate(rgb_src, [0.2]*3, [0.8]*3)
    return color_to_hex(rgb_dst)
