import atexit
import subprocess
import re
import os.path

class TestCase(object):
    @property
    def name(self):
        pass

    def generate(self, ctx, n):
        pass
    def run(self, ctx, n):
        pass

class PuppetTest(object):
    def __init__(self, name, generate):
        self.name = 'puppet-' + name
        self._generate = generate

    def manifest(self, ctx):
        return os.path.join(ctx.tmpdir, self.name + ".pp")

    def generate(self, ctx, n):
        with open(self.manifest(ctx), 'w') as fh:
            fh.write(self._generate(n))

    def run(self, ctx, n):
        env = dict(os.environ)
        env['BUNDLE_GEMFILE'] = os.path.join(
            os.environ.get('PUPPET_ROOT',
                           os.path.join(os.environ['HOME'], 'code', 'puppet')),
            'Gemfile')
        out = subprocess.check_output(
            ['bundle', 'exec', 'puppet', 'apply', '--color=false', self.manifest(ctx)],
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

class NodeRequireTest(object):
    @property
    def name(self):
        return "node-require"

    def generate(self, ctx, n):
        modules = os.path.join(ctx.tmpdir, "node_modules")
        os.mkdir(modules)
        for i in range(n):
            with open(os.path.join(modules, "file%08x.js" % (i,)), 'w') as fh:
                fh.write("function f() {}\n")

        with open(os.path.join(ctx.tmpdir, "main.js"), 'w') as fh:
            for i in range(n):
                fh.write("var f%08x = require('file%08x')\n" % (i, i))

    def run(self, ctx, n):
        subprocess.check_call(['node', os.path.join(ctx.tmpdir, "main.js")])

class PythonImportTest(object):
    @property
    def name(self):
        return "python-import"

    def generate(self, ctx, n):
        package = os.path.join(ctx.tmpdir, "benchimport")
        os.mkdir(package)

        for i in range(n):
            with open(os.path.join(package, "file%08x.py" % (i,)), 'w') as fh:
                fh.write("def f():\n  pass\n")

        with open(os.path.join(package, "__init__.py"), 'w') as fh:
            pass

        with open(os.path.join(ctx.tmpdir, "main.py"), 'w') as fh:
            for i in range(n):
                fh.write("from benchimport import file%08x\n" % (i,))

    def run(self, ctx, n):
        subprocess.check_call(['python', os.path.join(ctx.tmpdir, "main.py")])

class PythonImportRelativeTest(object):
    @property
    def name(self):
        return "python-import-relative"

    def generate(self, ctx, n):
        package = os.path.join(ctx.tmpdir, "benchimport")
        os.mkdir(package)

        for i in range(n):
            with open(os.path.join(package, "file%08x.py" % (i,)), 'w') as fh:
                fh.write("def f():\n  pass\n")

        with open(os.path.join(package, "__init__.py"), 'w') as fh:
            for i in range(n):
                fh.write("from . import file%08x\n" % (i,))

        with open(os.path.join(ctx.tmpdir, "main.py"), 'w') as fh:
            fh.write("import benchimport\n")

    def run(self, ctx, n):
        subprocess.check_call(['python', os.path.join(ctx.tmpdir, "main.py")])

class PythonImportManyTest(object):
    @property
    def name(self):
        return "python-import-many"

    def generate(self, ctx, n):
        for i in range(n):
            package = os.path.join(ctx.tmpdir, "bench%08x" % (i,))
            os.mkdir(package)
            with open(os.path.join(package, "__init__.py"), 'w') as fh:
                fh.write("def f():\n  pass\n")

        with open(os.path.join(ctx.tmpdir, "main.py"), 'w') as fh:
            for i in range(n):
                fh.write("import bench%08x\n" % (i,))

    def run(self, ctx, n):
        subprocess.check_call(['python', os.path.join(ctx.tmpdir, "main.py")])

class FileLookupTest(object):
    @property
    def name(self):
        return "lookup-file"

    def generate(self, ctx, n):
        for i in xrange(n):
            path = os.path.join(ctx.tmpdir, "file%08x" % (i,))
            with open(path, 'w') as fh:
                fh.write("%08x\n" % (i,))

    def run(self, ctx, n):
        for i in xrange(n):
            path = os.path.join(ctx.tmpdir, "file%08x" % (i,))
            with open(path) as fh:
                fh.read()

all_tests = dict(
    (t.name, t) for t in
    [
        PuppetTest('fanout-n', generate_fanout_n),
        PuppetTest('depth-n', generate_depth_n),
        NodeRequireTest(),
        PythonImportTest(),
        PythonImportRelativeTest(),
        PythonImportManyTest(),
        FileLookupTest()
    ]
)
