#!/usr/bin/env python3

"""A command-line tool to translate color schemes between dark- and light-background."""

import argparse

import cam
from color_io import color_to_decimal, color_to_hex, parse_color


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('colors', nargs='+',
                        help='the color(s) to translate, e.g. #ffffff or rgb(255, 255, 255)')
    parser.add_argument('--src-bg', choices=['dark', 'neutral', 'light'], default='neutral',
                        help='the background color type of the input colors.')
    parser.add_argument('--dst-bg', choices=['dark', 'neutral', 'light'], default='neutral',
                        help='the background color type to translate the input colors to.')
    parser.add_argument('--j-fac', type=float, default=1.0,
                        help='the factor to scale output lightness by.')
    parser.add_argument('--m-fac', type=float, default=1.0,
                        help='the factor to scale output colorfulness by.')
    parser.add_argument('--output-format', choices=['decimal', 'hex'], default='hex',
                        help='the output format desired.')
    return parser.parse_args()


def main():
    """The main function."""
    args = parse_args()
    cond_src = cam.get_conds(args.src_bg)
    cond_dst = cam.get_conds(args.dst_bg)
    output_fn = color_to_hex if args.output_format == 'hex' else color_to_decimal
    for color in args.colors:
        parsed = parse_color(color)
        translated = cam.translate(parsed, cond_src, cond_dst,
                                   J_factor=args.j_fac, M_factor=args.m_fac)
        print(output_fn(translated))


if __name__ == '__main__':
    main()
