#!/usr/bin/env python
import os
import sys
import time
import logging
import optparse
import errno
import itertools

import accidentallyquadratic

def run_one(tc, n):
    tc.generate(n)
    before = time.time()
    out = tc.run(n)
    after = time.time()
    if out is None:
        out = dict()
    out.update(n=n, total=(after-before))
    return out

def run_range(tc, ns, count):
    for n in ns:
        for i in xrange(count):
            result = run_one(tc, n)
            logging.info("test.run case=%s n=%d i=%d total=%f",
                         tc.name, n, i, result['total'])
            yield result

def render(fields, results, fh):
    fh.write(",".join(fields) + "\n")
    for result in results:
        vals = [str(result[f]) for f in fields]
        fh.write(",".join(vals))
        fh.write("\n")

def exps():
    i = 1
    while True:
        yield i
        yield i*2
        yield i*5
        i *= 10

def exprange(max):
    for r in exps():
        if r > max: break
        yield r

def main(args):
    parser = optparse.OptionParser("usage: %prog [OPTIONS] test")
    parser.add_option('-m', '--max',
                      dest='max',
                      default=1000,
                      help='max N to test until',
                      type='int')
    parser.add_option('-r', '--runs',
                      dest='runs',
                      default=3,
                      help='run each case how many times',
                      type='int')

    options, args = parser.parse_args(args)

    if len(args) != 2 or args[1] not in accidentallyquadratic.all_tests:
        print "Tests:"
        for t in accidentallyquadratic.all_tests:
            print " - %s" % (t)
        parser.error("You must specify a test to run.")
        return 1

    tc = accidentallyquadratic.all_tests[args[1]]()

    logging.basicConfig(level=logging.INFO)
    results = run_range(tc, exprange(options.max), options.runs)
    first = results.next()
    fields = first.keys()
    fields.remove('n')
    fields[:0] = ['n']
    try:
        os.makedirs('out')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    with open(os.path.join("out", tc.name + ".csv"), 'w') as fh:
        render(fields, itertools.chain([first], results), fh)

if __name__ == '__main__':
    exit(main(sys.argv))
