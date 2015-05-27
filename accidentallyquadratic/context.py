import tempfile
import shutil

class Context(object):
    def __init__(self):
        self.tmpdir = tempfile.mkdtemp(prefix='accidentallyquadratic-')

    def teardown(self):
        shutil.rmtree(self.tmpdir)
