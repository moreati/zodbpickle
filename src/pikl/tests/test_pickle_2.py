import copy_reg
import cStringIO
import io
import unittest
from cStringIO import StringIO

from .pickletester_2 import (AbstractPickleTests,
                             AbstractPickleModuleTests,
                             AbstractPersistentPicklerTests,
                             AbstractPicklerUnpicklerObjectTests,
                             BigmemPickleTests,
                             extension_codes,
                             has_c_implementation)

from test import test_support

class cStringIOMixin:
    output = input = cStringIO.StringIO

    def close(self, f):
        pass

class BytesIOMixin:
    output = input = io.BytesIO

    def close(self, f):
        pass

class FileIOMixin:

    def output(self):
        return open(test_support.TESTFN, 'wb+')

    def input(self, data):
        f = open(test_support.TESTFN, 'wb+')
        try:
            f.write(data)
            f.seek(0)
            return f
        except:
            f.close()
            raise

    def close(self, f):
        f.close()
        test_support.unlink(test_support.TESTFN)


class PickleBase(object):

    error = KeyError

    @property
    def module(self):
        from pikl import pickle_2
        return pickle_2


class PickleTests(AbstractPickleTests, AbstractPickleModuleTests, PickleBase):

    def dumps(self, arg, proto=2, fast=0):
        from pikl.pickle_2 import dumps
        # Ignore fast
        return dumps(arg, proto)

    def loads(self, buf):
        from pikl.pickle_2 import loads
        # Ignore fast
        return loads(buf)


class PicklerTests(AbstractPickleTests, PickleBase):

    def dumps(self, arg, proto=2, fast=0):
        from pikl.pickle_2 import Pickler
        f = cStringIO.StringIO()
        p = Pickler(f, proto)
        if fast:
            p.fast = fast
        p.dump(arg)
        f.seek(0)
        return f.read()

    def loads(self, buf):
        from pikl.pickle_2 import Unpickler
        f = cStringIO.StringIO(buf)
        u = Unpickler(f)
        return u.load()


class PersPicklerTests(AbstractPersistentPicklerTests):

    def dumps(self, arg, proto=2, fast=0):
        from pikl.pickle_2 import Pickler
        class PersPickler(Pickler):
            def persistent_id(subself, obj):
                return self.persistent_id(obj)
        f = cStringIO.StringIO()
        p = PersPickler(f, proto)
        if fast:
            p.fast = fast
        p.dump(arg)
        f.seek(0)
        return f.read()

    def loads(self, buf):
        from pikl.pickle_2 import Unpickler
        class PersUnpickler(Unpickler):
            def persistent_load(subself, obj):
                return self.persistent_load(obj)
        f = cStringIO.StringIO(buf)
        u = PersUnpickler(f)
        return u.load()


class PicklerUnpicklerObjectTests(AbstractPicklerUnpicklerObjectTests,
                                  PickleBase):

    @property
    def pickler_class(self):
        from pikl.pickle_2 import Pickler
        return  Pickler

    @property
    def unpickler_class(self):
        from pikl.pickle_2 import Unpickler
        return  Unpickler


class PickleBigmemPickleTests(BigmemPickleTests):

    def dumps(self, arg, proto=2, fast=0):
        from pikl import pickle_2
        # Ignore fast
        return pickle_2.dumps(arg, proto)

    def loads(self, buf):
        from pikl import pickle_2
        # Ignore fast
        return pickle_2.loads(buf)


class cPickleBase(object):

    @property
    def error(self):
        from pikl._pickle import BadPickleGet
        return BadPickleGet

    @property
    def module(self):
        from pikl import _pickle
        return _pickle


class cPickleTests(AbstractPickleTests,
                   AbstractPickleModuleTests,
                   cPickleBase,
                  ):
    def setUp(self):
        from pikl._pickle import dumps
        from pikl._pickle import loads
        self.dumps = dumps
        self.loads = loads


class cPicklePicklerTests(AbstractPickleTests, cPickleBase):

    def dumps(self, arg, proto=2):
        from pikl import _pickle
        f = self.output()
        try:
            p = _pickle.Pickler(f, proto)
            p.dump(arg)
            f.seek(0)
            return f.read()
        finally:
            self.close(f)

    def loads(self, buf):
        from pikl import _pickle
        f = self.input(buf)
        try:
            p = _pickle.Unpickler(f)
            return p.load()
        finally:
            self.close(f)

class cStringIOCPicklerTests(cStringIOMixin, cPicklePicklerTests):
    pass

class BytesIOCPicklerTests(BytesIOMixin, cPicklePicklerTests):
    pass

class FileIOCPicklerTests(FileIOMixin, cPicklePicklerTests):
    pass


class cPickleListPicklerTests(AbstractPickleTests, cPickleBase):

    def dumps(self, arg, proto=2):
        from pikl import _pickle
        p = _pickle.Pickler(proto)
        p.dump(arg)
        return p.getvalue()

    def loads(self, *args):
        from pikl import _pickle
        f = self.input(args[0])
        try:
            p = _pickle.Unpickler(f)
            return p.load()
        finally:
            self.close(f)

class cStringIOCPicklerListTests(cStringIOMixin, cPickleListPicklerTests):
    pass

class BytesIOCPicklerListTests(BytesIOMixin, cPickleListPicklerTests):
    pass

class FileIOCPicklerListTests(FileIOMixin, cPickleListPicklerTests):
    pass


class cPickleFastPicklerTests(AbstractPickleTests, cPickleBase):

    def dumps(self, arg, proto=2):
        from pikl import _pickle
        f = self.output()
        try:
            p = _pickle.Pickler(f, proto)
            p.fast = 1
            p.dump(arg)
            f.seek(0)
            return f.read()
        finally:
            self.close(f)

    def loads(self, *args):
        from pikl import _pickle
        f = self.input(args[0])
        try:
            p = _pickle.Unpickler(f)
            return p.load()
        finally:
            self.close(f)

    def test_recursive_list(self):
        self.assertRaises(ValueError,
                          AbstractPickleTests.test_recursive_list,
                          self)

    def test_recursive_tuple(self):
        self.assertRaises(ValueError,
                          AbstractPickleTests.test_recursive_tuple,
                          self)

    def test_recursive_inst(self):
        self.assertRaises(ValueError,
                          AbstractPickleTests.test_recursive_inst,
                          self)

    def test_recursive_dict(self):
        self.assertRaises(ValueError,
                          AbstractPickleTests.test_recursive_dict,
                          self)

    def test_recursive_multi(self):
        self.assertRaises(ValueError,
                          AbstractPickleTests.test_recursive_multi,
                          self)

    def test_nonrecursive_deep(self):
        # If it's not cyclic, it should pickle OK even if the nesting
        # depth exceeds PY_CPICKLE_FAST_LIMIT.  That happens to be
        # 50 today.  Jack Jansen reported stack overflow on Mac OS 9
        # at 64.
        a = []
        for i in range(60):
            a = [a]
        b = self.loads(self.dumps(a))
        self.assertEqual(a, b)

class cStringIOCPicklerFastTests(cStringIOMixin, cPickleFastPicklerTests):
    pass

class BytesIOCPicklerFastTests(BytesIOMixin, cPickleFastPicklerTests):
    pass

class FileIOCPicklerFastTests(FileIOMixin, cPickleFastPicklerTests):
    pass


class cPicklePicklerUnpicklerObjectTests(AbstractPicklerUnpicklerObjectTests,
                                         cPickleBase):

    @property
    def pickler_class(self):
        from pikl._pickle import Pickler
        return Pickler

    @property
    def unpickler_class(self):
        from pikl._pickle import Unpickler
        return Unpickler

class cPickleBigmemPickleTests(BigmemPickleTests):

    def dumps(self, arg, proto=2, fast=0):
        from pikl import _pickle
        # Ignore fast
        return _pickle.dumps(arg, proto)

    def loads(self, buf):
        from pikl import _pickle
        # Ignore fast
        return _pickle.loads(buf)


class Node(object):
    pass

copy_reg.add_extension(__name__, "Node", extension_codes.next())

class cPickleDeepRecursive(unittest.TestCase):

    def test_issue2702(self):
        # This should raise a RecursionLimit but in some
        # platforms (FreeBSD, win32) sometimes raises KeyError instead,
        # or just silently terminates the interpreter (=crashes).
        from pikl import _pickle
        nodes = [Node() for i in range(500)]
        for n in nodes:
            n.connections = list(nodes)
            n.connections.remove(n)
        self.assertRaises((AttributeError, RuntimeError), _pickle.dumps, n)

    def test_issue3179(self):
        # Safe test, because I broke this case when fixing the
        # behaviour for the previous test.
        from pikl import _pickle
        res=[]
        for x in range(1,2000):
            res.append(dict(doc=x, similar=[]))
        _pickle.dumps(res)


def test_suite():
    import unittest
    tests = [
        unittest.makeSuite(PickleTests),
        unittest.makeSuite(PicklerTests),
        unittest.makeSuite(PersPicklerTests),
        unittest.makeSuite(PicklerUnpicklerObjectTests),
        unittest.makeSuite(PickleBigmemPickleTests),
	]

    if has_c_implementation:
        tests.extend([
            unittest.makeSuite(cPickleTests),
            unittest.makeSuite(cStringIOCPicklerTests),
            unittest.makeSuite(BytesIOCPicklerTests),
            unittest.makeSuite(FileIOCPicklerTests),
            unittest.makeSuite(cStringIOCPicklerListTests),
            unittest.makeSuite(BytesIOCPicklerListTests),
            unittest.makeSuite(FileIOCPicklerListTests),
            unittest.makeSuite(cStringIOCPicklerFastTests),
            unittest.makeSuite(BytesIOCPicklerFastTests),
            unittest.makeSuite(FileIOCPicklerFastTests),
            unittest.makeSuite(cPickleDeepRecursive),
            unittest.makeSuite(cPicklePicklerUnpicklerObjectTests),
            unittest.makeSuite(cPickleBigmemPickleTests),
        ])
    return unittest.TestSuite(tests)

if __name__ == '__main__':
    test_support.run_unittest(test_suite())
