import pytest
import unittest

from TrivialUI import DictModel, DictProxy, LeafProxy

def satisfies_QAbstractItemModel(thing):
    assert hasattr(thing, "index")
    assert hasattr(thing, "parent")
    assert hasattr(thing, "rowCount")
    assert hasattr(thing, "columnCount")
    assert hasattr(thing, "data")

class TestDictEntryProxy(unittest.TestCase):
    def test_dictProxy(self):
        proxy = DictProxy('key', {'a': 1, 'b': 2})

        assert proxy.hasChild(0)
        assert proxy.hasChild(1)
        assert not proxy.hasChild(2)

        self.assertIsInstance(proxy.childAt(0), LeafProxy)
        self.assertEqual(set(['a', 'b']),
                         set([proxy.childAt(i).key
                              for i in range(2)]))
        self.assertEqual(set([1, 2]),
                         set([proxy.childAt(i).data
                              for i in range(2)]))
        self.assertEqual(proxy, proxy.childAt(0).parent)
    
    def test_create(self):
        the_dict = {'first': {'one': 1, 'two': 2, 'three': 3},
                    'second': {'une': 1, 'deux': 2, 'trois': 3}}

        proxy = DictModel(the_dict)

        satisfies_QAbstractItemModel(proxy)
