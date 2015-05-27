import tempfile
import shutil
from contextlib import contextmanager

class Context(object):
    def __init__(self):
        self.tmpdir = tempfile.mkdtemp(prefix='accidentallyquadratic-')

    def teardown(self):
        shutil.rmtree(self.tmpdir)

@contextmanager
def context():
    c = Context()
    try:
        yield c
    finally:
        c.teardown()
