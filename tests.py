#!/usr/bin/env python
import os
import sys
import tempfile
import time
import subprocess
import re
import logging
import shutil
import optparse

class TestCase(object):
    @property
    def name(self):
        pass

    def generate(self, n):
        pass
    def run(self, n):
        pass

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

class PuppetTest(object):
    def __init__(self, name, generate):
        self.name = 'puppet-' + name
        self.tmpdir = tempfile.mkdtemp(suffix=name, prefix='aq-puppet-')
        self.manifest = os.path.join(self.tmpdir, name + ".pp")
        self._generate = generate

    def generate(self, n):
        with open(self.manifest, 'w') as fh:
            fh.write(self._generate(n))

    def run(self, n):
        env = dict(os.environ)
        env['BUNDLE_GEMFILE'] = os.path.join(os.environ['HOME'], 'code', 'puppet', 'Gemfile')
        out = subprocess.check_output(
            ['bundle', 'exec', 'puppet', 'apply', '--color=false', self.manifest],
            env=env)

        matches = re.findall(r'^Notice: ([^\n]+) in ([0-9.]+) seconds$',
                             out, re.S | re.M)
        times = {}
        if matches[0][0].startswith('Compiled catalog'):
            times['compile'] = float(matches[0][1])
        if matches[1][0].startswith('Applied catalog'):
            times['apply'] = float(matches[1][1])
        return times

    def teardown(self):
        shutil.rmtree(self.tmpdir)


def generate_depth_n(n):
    lines = [
        r'define object() {}',
        r'node default {'
        r'object { "%08x": }' % (0,)
    ]
    for i in xrange(1, n):
        lines.append(r'  object { "%08x": require => Object["%08x"] }' % (i, i-1))
    lines.append(r'}')
    return "\n".join(lines)


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

    logging.basicConfig(level=logging.INFO)
    tc = PuppetTest('depth-n', generate_depth_n)
    try:
        with open(os.path.join("out", tc.name + ".csv"), 'w') as fh:
            results = run_range(tc, exprange(options.max), options.runs)
            render(results, fh)
    finally:
        tc.teardown()


if __name__ == '__main__':
    exit(main(sys.argv))
