#!/usr/bin/env python3

"""Benchmarks different optimization methods for gamut mapping."""

from functools import partial
import time

import numpy as np
from scipy import optimize

import cam


try:
    import sys
    from IPython.core.ultratb import AutoFormattedTB
    sys.excepthook = AutoFormattedTB('Plain', 'Neutral')
except ImportError:
    pass


def proj(x):
    """Projects x onto the feasible set."""
    return np.clip(x, 0, 1)


def grad(loss, x):
    """Computes the gradient of loss at x using finite differences."""
    return optimize.approx_fprime(x, loss, 1e-8)


def method_lbfgsb(rgb, loss):
    """L-BFGS-B from scipy.optimize."""
    x = proj(rgb)
    x_opt, _, _ = optimize.fmin_l_bfgs_b(loss, x, approx_grad=True, bounds=[(0, 1)]*3)
    return x_opt


def method_tnc(rgb, loss):
    """Truncated Newton from scipy.optimize."""
    x = proj(rgb)
    x_opt, _, _ = optimize.fmin_tnc(loss, x, approx_grad=True, bounds=[(0, 1)]*3, disp=0)
    return x_opt


def method_de(rgb, loss):
    """Differential Evolution from scipy.optimize."""
    result = optimize.differential_evolution(loss, [(0, 1)]*3, polish=False)
    return result.x


def method_grad(rgb, loss):
    """Projected gradient descent."""
    x = proj(rgb)
    last_x = None
    i = 0
    while last_x is None or np.mean(abs(x - last_x)) >= 1e-4:
        if i >= 200:
            break
        last_x = x
        g = grad(loss, x)
        x = proj(x - 0.25 * g)
        i += 1
    return x


def method_grad2(rgb, loss):
    """Projected gradient descent."""
    x = proj(rgb)
    last_x = None
    i = 0
    while last_x is None or np.mean(abs(x - last_x)) >= 1e-4:
        if i >= 200:
            break
        last_x = x
        l = loss(x)
        g = grad(loss, x)
        ss = 10
        ll = np.inf
        while ll > l:
            ss /= 2
            ll = loss(proj(x - ss * g))
        x = proj(x - ss * g)
        i += 1
    return x


def method_grad_bb(rgb, loss):
    """Projected gradient descent with Barzilai-Borwein step size."""
    x = proj(rgb)
    last_g, last_x = None, None
    i = 0
    while last_x is None or np.mean(abs(x - last_x)) >= 1e-4:
        if i >= 200:
            break
        g = grad(loss, x)
        if last_x is not None:
            s = x - last_x
            y = g - last_g
            ss = np.sum(s*s) / np.sum(s*y)
        else:
            ss = 1e-3
        last_g, last_x = g, x
        x = proj(x - ss * g)
        i += 1
    return x


def method_adagrad(rgb, loss):
    """Projected AdaGrad."""
    x = proj(rgb)
    last_x = None
    g2 = np.zeros_like(x) + 1e-8
    while last_x is None or np.mean(abs(x - last_x)) >= 1e-4:
        last_x = x
        g = grad(loss, x)
        g2 += g**2
        x = proj(x - 0.25 * g / np.sqrt(g2))
    return x


def method_cd(rgb, loss):
    """Coordinate descent."""
    x = proj(rgb)
    last_x = None
    coord = 0
    e = np.eye(3)
    while last_x is None or np.mean(abs(x - last_x)) >= 1e-4:
        last_x = x
        ss = optimize.brent(lambda ss: loss(proj(x - e[coord] * ss)))
        x = proj(x - e[coord] * ss)
        coord = (coord + 1) % 3
    return x


def main():
    """The main function."""
    np.random.seed(0)
    data = np.zeros((256, 3))
    i = 0
    while i < len(data):
        data[i] = np.random.normal(loc=0.5, size=3)
        if (proj(data[i]) != data[i]).any():
            i += 1
    print('Dataset generated. Size: %d.' % len(data))

    methods = [method_lbfgsb, method_adagrad]
    for method in methods:
        total_loss = 0
        started_at = time.perf_counter()
        for rgb in data:
            loss = partial(cam.distance, rgb)
            rgb_opt = method(rgb, loss)
            total_loss += loss(rgb_opt)
        time_taken = time.perf_counter() - started_at
        print('%s %.3f s, loss: %g' % (method.__name__, time_taken, total_loss))

if __name__ == '__main__':
    main()
