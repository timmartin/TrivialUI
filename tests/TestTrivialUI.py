import pytest

from TrivialUI import DictModel, DictProxy

def satisfies_QAbstractItemModel(thing):
    assert hasattr(thing, "index")
    assert hasattr(thing, "parent")
    assert hasattr(thing, "rowCount")
    assert hasattr(thing, "columnCount")
    assert hasattr(thing, "data")

class TestDictEntryProxy(object):
    def test_dictProxy(self):
        proxy = DictProxy({'a': 1, 'b': 2})

        assert proxy.hasChild(0)
        assert proxy.hasChild(1)
        assert not proxy.hasChild(2)

        assert set([1, 2]) == set([proxy.childAt(0).data,
                                   proxy.childAt(1).data])
    
    def test_create(self):
        the_dict = {'first': {'one': 1, 'two': 2, 'three': 3},
                    'second': {'une': 1, 'deux': 2, 'trois': 3}}

        proxy = DictModel(the_dict)

        satisfies_QAbstractItemModel(proxy)
