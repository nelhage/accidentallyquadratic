#!/usr/bin/env python
# -*- coding: utf-8; -*-
import matplotlib.pyplot as plt
import numpy
import sys
import re
from collections import defaultdict
import optparse

parser = optparse.OptionParser()
parser.add_option("-f", "--fields",
                  dest='fields',
                  default='',
                  help='which fields to graph')
parser.add_option("-o", "--output",
                  dest='output',
                  default='out.png',
                  help='output filename')
options, args = parser.parse_args()

data = defaultdict(list)

with open(args[0]) as f:
    labels = f.readline().strip().split(",")
    for l in f.readlines():
        if not l:
            continue
        bits = l.split(",")
        k = int(bits[0])
        data[k].append(
            dict(zip(labels[1:], map(float, bits[1:]))))

x = sorted(data.keys())

xmin = 0
xmax = int(1.1 * max(x))

plt.xlim([xmin, xmax])
plt.ylabel(label[0])
plt.xlabel('nodes')

if options.fields:
    fields = options.fields().split(",")
else:
    fields = labels[1:]

for field in fields:
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

    lerr = sum(pow(linear(xx) - yy, 2) for (xx,yy) in zip(x,y))
    qerr = sum(pow(quadratic(xx) - yy, 2) for (xx,yy) in zip(x,y))
    print "%s: error linear=%f quadratic=%f" % (field, lerr, qerr)

    plt.errorbar(x, y, yerr=err,
                 marker='.',
                 linestyle='none',
                 label=field)

    xs = range(xmin, xmax, xmax/100)
    if lerr < 2 * qerr:
        plt.plot(xs, map(linear, xs))
    else:
        plt.plot(xs, map(quadratic, xs))

plt.legend(loc=2)
plt.savefig(options.output)
