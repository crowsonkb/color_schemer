"""Converts between the sRGB and CIECAM02 JCh (lightness/chroma/hue) color spaces.

See https://en.wikipedia.org/wiki/SRGB and https://en.wikipedia.org/wiki/CIECAM02. 'sRGB' here is
defined as an RGB color space with the sRGB primaries and gamma 2.2 - i.e. it does not use the
piecewise sRGB transfer function but goes with the most common actual implementation of sRGB in
display hardware.
"""

import colour
import numpy as np


def sRGB_to_JCh(RGB, RGB_b, surround='average', epsilon=1e-6):
    """Converts an sRGB foreground color to CIECAM02 JCh (lightness/chroma/hue).

    Input sRGB values are nonlinear and range from 0 to 1.

    Args:
        RGB: The foreground color sRGB value.
        RGB_b: The background color sRGB value.
        surround: The CIECAM02 viewing conditions.
        epsilon: A numerical fuzz factor to use in place of true black.

    Returns:
        The converted foreground color in JCh space.
    """
    RGB_linear = np.maximum(epsilon, np.float64(RGB)**2.2)
    RGB_b_linear = np.maximum(epsilon, np.float64(RGB_b)**2.2)
    XYZ = colour.sRGB_to_XYZ(RGB_linear, apply_decoding_cctf=False) * 100
    XYZ_w = colour.sRGB_to_XYZ([1, 1, 1], apply_decoding_cctf=False) * 100
    L_A = 20
    Y_b = colour.sRGB_to_XYZ(RGB_b_linear, apply_decoding_cctf=False)[1] * 100
    if isinstance(surround, str):
        surround = colour.appearance.ciecam02.CIECAM02_VIEWING_CONDITIONS[surround]
    return np.float64(colour.XYZ_to_CIECAM02(XYZ, XYZ_w, L_A, Y_b, surround, True)[:3])


def JCh_to_sRGB(JCh, RGB_b, surround='average', epsilon=1e-6):
    """Converts a CIECAM02 JCh (lightness/chroma/hue) foreground color to sRGB.

    Input and output sRGB values are nonlinear and range from 0 to 1. This routine will clamp
    output RGB values to (0, 1] rather than generate an out-of-gamut color.

    Args:
        JCh: The foreground color JCh value. Can come from sRGB_to_JCh().
        RGB_b: The background color sRGB value.
        surround: The CIECAM02 viewing conditions.
        epsilon: A numerical fuzz factor to use in place of true black.

    Returns:
        The converted foreground color in sRGB space.
    """
    J, C, h = JCh
    RGB_b_linear = np.maximum(epsilon, np.float64(RGB_b)**2.2)
    XYZ_w = colour.sRGB_to_XYZ([1, 1, 1], apply_decoding_cctf=False) * 100
    L_A = 20
    Y_b = colour.sRGB_to_XYZ(RGB_b_linear, apply_decoding_cctf=False)[1] * 100
    if isinstance(surround, str):
        surround = colour.appearance.ciecam02.CIECAM02_VIEWING_CONDITIONS[surround]
    XYZ = colour.CIECAM02_to_XYZ(J, C, h, XYZ_w, L_A, Y_b, surround, True) / 100
    return np.clip(colour.XYZ_to_sRGB(XYZ, apply_encoding_cctf=False), 0, 1)**(1 / 2.2)


def translate(fg, bg_src, bg_dst, J_factor=1, C_factor=1):
    """Returns a foreground color, intended for use on bg_dst, that appears like the given
    foreground color on background bg_src.

    Args:
        fg: The foreground color sRGB value to translate.
        bg_src: The source background sRGB value.
        bg_dst: The destination background sRGB value.
        J_factor: Scales output lightness by this factor.
        C_factor: Scales output chroma by this factor.
    """
    JCh = sRGB_to_JCh(fg, bg_src)
    JCh[0] *= J_factor
    JCh[1] *= C_factor
    return JCh_to_sRGB(JCh, bg_dst)
