import atexit
import shutil
import subprocess
import tempfile
import re
import os.path

class TestCase(object):
    @property
    def name(self):
        pass

    def generate(self, n):
        pass
    def run(self, n):
        pass

class PuppetTest(object):
    def __init__(self, name, generate):
        self.name = 'puppet-' + name
        self.tmpdir = tempfile.mkdtemp(suffix=name, prefix='aq-puppet-')
        self.manifest = os.path.join(self.tmpdir, name + ".pp")
        self._generate = generate
        atexit.register(lambda: shutil.rmtree(self.tmpdir))

    def generate(self, n):
        with open(self.manifest, 'w') as fh:
            fh.write(self._generate(n))

    def run(self, n):
        env = dict(os.environ)
        env['BUNDLE_GEMFILE'] = os.path.join(
            os.environ.get('PUPPET_ROOT', 
                           os.path.join(os.environ['HOME'], 'code', 'puppet')), 
            'Gemfile')
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

def generate_fanout_n(n):
    lines = [
        r'define object() {}',
        r'node default {'
    ]
    for i in xrange(1, n):
        lines.append(r'  object { "%08x": }' % (i,))
    lines.append(r'}')
    return "\n".join(lines)

all_tests = {
    'puppet.fanout-n': lambda: PuppetTest('fanout-n', generate_fanout_n),
    'puppet.depth-n': lambda: PuppetTest('depth-n', generate_depth_n),
}
