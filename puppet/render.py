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
        name = bits[0]
        k = int(re.search('/bench(\d+)\.pp', name).group(1))
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

quadratic = numpy.poly1d(numpy.polyfit(x, y, 2))

xmin = 0
xmax = int(1.1 * max(x))

plt.errorbar(x, y, yerr=err, marker='.', linestyle='none')
plt.xlim([xmin, xmax])
plt.ylabel('runtime')
plt.xlabel('nodes')

xs = range(xmin, xmax, xmax/100)
plt.plot(xs, map(quadratic, xs), label='x²')

plt.savefig('puppet.png')
