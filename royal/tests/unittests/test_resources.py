import unittest
from pyramid.testing import DummyRequest


class Test(unittest.TestCase):

    def check_assertions(self, cls, name, parent=None):
        b = cls(name, parent)
        if parent is None:
            root = b
        else:
            root = parent.root
        self.assertEqual(b.__name__, name)
        self.assertEqual(parent, b.__parent__)
        self.assertIs(root, b.root)
        return b

    def test_base(self):
        from royal.resource import Base
        self.check_assertions(Base, 'name')

    def test_root(self):
        from royal.resource import Root
        request = DummyRequest()
        root = Root(request)

        self.assertEqual(request, root.request)
        self.assertIsNone(root.__parent__)
        self.assertEqual('', root.__name__)
        self.assertEqual(root, root.root)

    def test_collection(self):
        from royal.resource import Collection, Root
        from royal.exceptions import MethodNotAllowed
        request = DummyRequest()
        root = Root(request)
        collection = self.check_assertions(Collection, 'users', root)
        with self.assertRaises(MethodNotAllowed):
            collection.index()
        with self.assertRaises(MethodNotAllowed):
            collection.create([])
        with self.assertRaises(MethodNotAllowed):
            collection.delete()

    def test_resource(self):
        from royal.resource import Collection, Item, Root
        from royal.exceptions import MethodNotAllowed
        request = DummyRequest()
        root = Root(request)
        c = Collection('users', root)
        resource = self.check_assertions(Item, 'hadrien', parent=c)

        with self.assertRaises(MethodNotAllowed):
            resource.show()
        with self.assertRaises(MethodNotAllowed):
            resource.delete()
        with self.assertRaises(MethodNotAllowed):
            resource.replace()
        with self.assertRaises(MethodNotAllowed):
            resource.update()
