"""Converts between the sRGB and CIECAM02 JCh (lightness/chroma/hue) color spaces.

See https://en.wikipedia.org/wiki/SRGB and https://en.wikipedia.org/wiki/CIECAM02. 'sRGB' here is
defined as an RGB color space with the sRGB primaries and gamma 2.2 - i.e. it does not use the
piecewise sRGB transfer function but goes with the most common actual implementation of sRGB in
display hardware.
"""

from functools import partial

import colour
import numpy as np
from scipy import optimize


def sRGB_to_XYZ(RGB):
    """Converts an sRGB color (nonlinear, range 0-1) to XYZ using a gamma=2.2 transfer function.

    Args:
        RGB (array_like): The sRGB color.

    Returns:
        np.ndarray: The XYZ color.
    """
    RGB = np.array(RGB)
    RGB_linear = np.sign(RGB) * abs(RGB)**2.2
    return colour.sRGB_to_XYZ(RGB_linear, apply_decoding_cctf=False)


def XYZ_to_sRGB(XYZ):
    """Converts an XYZ color to sRGB (nonlinear, range 0-1) using a gamma=2.2 transfer function.

    Args:
        XYZ (array_like): The XYZ color.

    Returns:
        np.ndarray: The sRGB color.
    """
    XYZ = np.array(XYZ)
    RGB_linear = colour.XYZ_to_sRGB(XYZ, apply_encoding_cctf=False)
    return np.sign(RGB_linear) * abs(RGB_linear)**(1/2.2)


def distance(RGB_1, RGB_2):
    """Returns the squared distance between two sRGB colors.

    Args:
        RGB_1 (np.ndarray): The first color.
        RGB_2 (np.ndarray): The second color.

    Returns:
        float: The squared distance between the two colors.
    """
    IPT_1 = colour.XYZ_to_IPT(sRGB_to_XYZ(RGB_1))
    IPT_2 = colour.XYZ_to_IPT(sRGB_to_XYZ(RGB_2))
    return np.sum(np.square(IPT_1 - IPT_2))


def gamut_map(RGB):
    """Finds the nearest in-gamut color to an out-of-gamut color.

    Args:
        RGB (np.ndarray): The input RGB color.

    Returns:
        np.ndarray: The gamut-mapped RGB color.
    """
    x = np.clip(RGB, 0, 1)
    if (RGB == x).all():
        return x
    loss = partial(distance, RGB)
    x_opt, _, _ = optimize.fmin_l_bfgs_b(loss, x, approx_grad=True, bounds=[(0, 1)]*3)
    return x_opt


def sRGB_to_JCh(RGB, RGB_b, surround='average'):
    """Converts an sRGB foreground color to CIECAM02 JCh (lightness/chroma/hue).

    Input sRGB values are nonlinear and range from 0 to 1.

    Args:
        RGB (array_like): The foreground color sRGB value.
        RGB_b (array_like): The background color sRGB value.
        surround (str): The CIECAM02 viewing conditions.

    Returns:
        np.ndarray: The converted foreground color in JCh space.
    """
    XYZ = sRGB_to_XYZ(RGB) * 100
    XYZ_w = sRGB_to_XYZ([1, 1, 1]) * 100
    L_A = 20
    Y_b = sRGB_to_XYZ(RGB_b)[1] * 100
    if isinstance(surround, str):
        surround = colour.appearance.ciecam02.CIECAM02_VIEWING_CONDITIONS[surround]
    return np.float64(colour.XYZ_to_CIECAM02(XYZ, XYZ_w, L_A, Y_b, surround, True)[:3])


def JCh_to_sRGB(JCh, RGB_b, surround='average'):
    """Converts a CIECAM02 JCh (lightness/chroma/hue) foreground color to sRGB.

    Input and output sRGB values are nonlinear and range from 0 to 1. This routine will perform
    gamut mapping on out-of-gamut sRGB values.

    Args:
        JCh (array_like): The foreground color JCh value. Can come from sRGB_to_JCh().
        RGB_b (array_like): The background color sRGB value.
        surround (str): The CIECAM02 viewing conditions.

    Returns:
        np.ndarray: The converted foreground color in sRGB space.
    """
    J, C, h = JCh
    XYZ_w = sRGB_to_XYZ([1, 1, 1]) * 100
    L_A = 20
    Y_b = sRGB_to_XYZ(RGB_b)[1] * 100
    if isinstance(surround, str):
        surround = colour.appearance.ciecam02.CIECAM02_VIEWING_CONDITIONS[surround]
    XYZ = colour.CIECAM02_to_XYZ(J, C, h, XYZ_w, L_A, Y_b, surround, True) / 100
    RGB = XYZ_to_sRGB(XYZ)
    if RGB.ndim == 1:
        return gamut_map(RGB)
    RGB_in_gamut = np.zeros_like(RGB)
    for i, rgb in enumerate(RGB):
        RGB_in_gamut[i, :] = gamut_map(rgb)
    return RGB_in_gamut


def translate(fg, bg_src, bg_dst, J_factor=1, C_factor=1):
    """Returns a foreground color, intended for use on bg_dst, that appears like the given
    foreground color on background bg_src.

    Args:
        fg (array_like): The foreground color sRGB value to translate.
        bg_src (array_like): The source background sRGB value.
        bg_dst (array_like): The destination background sRGB value.
        J_factor (float): Scales output lightness by this factor.
        C_factor (float): Scales output chroma by this factor.

    Returns:
        np.ndarray: The converted foreground color in sRGB space.
    """
    JCh = sRGB_to_JCh(fg, bg_src)
    JCh[0] *= J_factor
    JCh[1] *= C_factor
    return JCh_to_sRGB(JCh, bg_dst)
