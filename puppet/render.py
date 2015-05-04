#!/usr/bin/env python
# -*- coding: utf-8; -*-
import matplotlib.pyplot as plt
import numpy
import sys
import re
from collections import defaultdict

data = defaultdict(list)

with open(sys.argv[1]) as f:
    for l in f.readlines():
        if not l:
            continue
        bits = l.split()
        k = int(bits[0])
        data[k].append(dict(compile=float(bits[1]),
                            apply=float(bits[2]),
                            total=float(bits[3])))

x = sorted(data.keys())
y = []
err = [[], []]
for v in x:
    vals = [pt['total'] for pt in data[v]]
    mean = sum(vals) / len(vals)
    y.append(mean)
    err[0].append(mean - min(vals))
    err[1].append(max(vals) - mean)

linear = numpy.poly1d(numpy.polyfit(x, y, 1))
quadratic = numpy.poly1d(numpy.polyfit(x, y, 2))

xmin = 0
xmax = int(1.1 * max(x))

plt.errorbar(x, y, yerr=err, marker='.', linestyle='none')
plt.xlim([xmin, xmax])
plt.ylim([0, max(y) * 1.3])
plt.ylabel('runtime')
plt.xlabel('nodes')

xs = range(xmin, xmax, xmax/100)
plt.plot(xs, map(quadratic, xs), label='x²')
plt.plot(xs, map(linear, xs), label='x')

plt.savefig('puppet.png')
