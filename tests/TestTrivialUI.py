from PySide import QtCore
import pytest
import unittest

from TrivialUI import DictModel, ListModel, DictProxy, ListProxy, LeafProxy

def satisfies_QAbstractItemModel(thing):
    assert hasattr(thing, "index")
    assert hasattr(thing, "parent")
    assert hasattr(thing, "rowCount")
    assert hasattr(thing, "columnCount")
    assert hasattr(thing, "data")

class TestDictProxy(unittest.TestCase):
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


class TestDictModel(unittest.TestCase):
    def test_create(self):
        the_dict = {'first': {'one': 1, 'two': 2, 'three': 3},
                    'second': {'une': 1, 'deux': 2, 'trois': 3}}

        model = DictModel(the_dict)

        satisfies_QAbstractItemModel(model)

        self.assertEquals(2, model.rowCount(QtCore.QModelIndex()))


class TestListModel(unittest.TestCase):
    def test_create(self):
        the_list = [('first', None, [('one', 1), ('two', 2)]),
                    ('second', None, [('une', 1), ('deux', 2)])]

        model = ListModel(the_list)

        satisfies_QAbstractItemModel(model)

        self.assertEquals(2, model.rowCount(QtCore.QModelIndex()))

        root_index = model.index(0, 0, QtCore.QModelIndex())

        self.assertEquals(2, model.rowCount(root_index))
        self.assertEquals('first',
                          model.data(root_index, QtCore.Qt.DisplayRole))

        first_child_index = model.index(0, 0, root_index)
        self.assertEquals(0, model.rowCount(first_child_index))
