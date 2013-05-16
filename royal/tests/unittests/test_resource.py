import unittest


class TestBase(unittest.TestCase):

    def test_ancestor_no_parent(self):
        from royal.resource import Resource

        base = Resource('name', None)

        self.assertEqual({}, base.ancestors)

    def test_ancestor_with_resource_parent(self):
        from royal.resource import Resource

        dad = Resource('dad', None)

        kid = Resource('kid', dad)

        self.assertEqual({'dad': dad}, kid.ancestors)

    def test_ancestor_with_collection_parent(self):
        from royal.resource import Resource, Collection

        singers = Collection('singers', None)

        bob_marley = Resource('bob_marley', singers)

        songs = Collection('songs', bob_marley)

        trenchtown = Resource('trench_town_rock', songs)

        self.assertEqual({'singers': bob_marley}, trenchtown.ancestors)
