#!/usr/bin/env python
import os
import sys
import time
import logging
import optparse

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
    out = []
    for n in ns:
        for i in xrange(count):
            out.append(run_one(tc, n))
            logging.info("test.run case=%s n=%d i=%d total=%f",
                         tc.name, n, i, out[-1]['total'])
    return out

def render(results, fh):
    fields = results[0].keys()
    fields.remove('n')
    fields[:0] = ['n']
    fh.write(",".join(fields) + "\n")
    for result in results:
        vals = [str(result[f]) for f in fields]
        fh.write(",".join(vals))
        fh.write("\n")

def exprange(max):
    i = 1
    while i < max:
        yield i
        yield 2*i
        yield 5*i
        i *= 10

def main(args):
    parser = optparse.OptionParser()
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

    if len(args) != 1 or args[0] not in accidentallyquadratic.all_tests:
        print "usage: %s [OPTIONS] test" % (sys.argv[0],)
        print "Tests:"
        for t in accidentallyquadratic.all_tests:
            print " - %s" % (t)
        parser.usage()
        return 1

    tc = accidentallyquadratic.all_tests[args[1]]()

    logging.basicConfig(level=logging.INFO)
    try:
        with open(os.path.join("out", tc.name + ".csv"), 'w') as fh:
            results = run_range(tc, exprange(options.max), options.runs)
            render(results, fh)
    finally:
        tc.teardown()

if __name__ == '__main__':
    exit(main(sys.argv))
