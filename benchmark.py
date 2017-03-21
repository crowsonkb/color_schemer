#!/usr/bin/env python3

"""Benchmarks app.py and its HTTP server."""

from concurrent.futures import ThreadPoolExecutor
import os
import sys
import time

import numpy as np
import requests


def timeit(run_for=1):
    def call(fn):
        def record_times(*args, **kwargs):
            times = [time.perf_counter()]
            while times[-1] - times[0] < run_for:
                fn(*args, **kwargs)
                times.append(time.perf_counter())
            return np.diff(times)
        return record_times
    return call


def main():
    base_url = 'http://127.0.0.1:8000/'
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    form = dict(colors='', direction='to_dark', J_factor=1, C_factor=1)
    for _ in range(256):
        r, g, b = np.random.randint(256, size=3)
        form['colors'] += 'rgb(%d, %d, %d)\n' % (r, g, b)

    @timeit(run_for=2.5)
    def get_result():
        r = requests.post(base_url + 'result', data=form)
        r.raise_for_status()
        _ = r.text

    diffs = []
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
        futs = [ex.submit(get_result) for _ in range(10)]
        for fut in futs:
            diffs.extend(fut.result())

    diffs_ = np.array(diffs) * 1000
    print('%d requests made.' % len(diffs_))
    print('median: %.3f ms' % np.median(diffs_))
    print('90th %%: %.3f ms' % np.percentile(diffs_, 90))
    print('99th %%: %.3f ms' % np.percentile(diffs_, 99))

if __name__ == '__main__':
    main()
