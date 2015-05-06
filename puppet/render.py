#!/usr/bin/env python
# -*- coding: utf-8; -*-
import matplotlib.pyplot as plt
import numpy
import sys
import re
from collections import defaultdict
import optparse

parser = optparse.OptionParser()
parser.add_option("--fields",
                  dest='fields',
                  default='compile,apply,total',
                  help='which fields to graph')
parser.add_option("-o", "--output",
                  dest='output',
                  default='puppet.png',
                  help='output filename')
options, args = parser.parse_args()

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

xmin = 0
xmax = int(1.1 * max(x))

plt.xlim([xmin, xmax])
plt.ylabel('runtime')
plt.xlabel('nodes')

for field in options.fields.split(','):
    y = []
    err = [[], []]
    for v in x:
        vals = [pt[field] for pt in data[v]]
        mean = sum(vals) / len(vals)
        y.append(mean)
        err[0].append(mean - min(vals))
        err[1].append(max(vals) - mean)

    linear = numpy.poly1d(numpy.polyfit(x, y, 1))
    quadratic = numpy.poly1d(numpy.polyfit(x, y, 2))

    plt.errorbar(x, y, yerr=err,
                 marker='.',
                 linestyle='none',
                 label=field)

    xs = range(xmin, xmax, xmax/100)
    plt.plot(xs, map(quadratic, xs))
    plt.plot(xs, map(linear, xs))

plt.legend(loc=2)
plt.savefig(options.output)
