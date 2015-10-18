from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtWidgets import QMainWindow, QTreeView
import collections

class DictProxy(object):
    def __init__(self, key, data, parent=None, row=0):
        self.data = data
        self.key = key
        self.parent = parent
        self.row = row
        self.child_cache = {}

    def hasChild(self, row):
        """Check whether this dict has an entry for the specified row. In
        fact, this just checks whether the number of entries in the
        dict is sufficient.
        """

        return row < len(self.data)

    def childAt(self, row):
        if row in self.child_cache:
            return self.child_cache[row]
        else:
            items = list(self.data.items())
            key, childItem = items[row]
            if isinstance(childItem, dict):
                child = DictProxy(key, childItem, self, row)
            else:
                child = LeafProxy(key, childItem, self)
            self.child_cache[row] = child
            return child

    def childCount(self):
        return len(self.data)


class ListProxy(object):
    def __init__(self, key, click_target, data, parent=None, row=0):
        """
        :param click_target:  The object that, if this row of the view
          is clicked on, will be passed to the click handler.
        :param row:  The row of this list in its parent.
        """
        self.data = data
        self.key = key
        self.click_target = click_target
        self.parent = parent
        self.row = row

        self.child_cache = {}

    def has_child(self, row):
        return row < len(self.data)

    def child_at(self, row):
        if row in self.child_cache:
            return self.child_cache[row]
        else:
            if isinstance(self.data[row], tuple):
                key, click_target, children = self.data[row]
                child = ListProxy(key, click_target, children, self)
            else:
                child = LeafProxy(self.data[row], self.data[row], [], self)
            self.child_cache[row] = child
            return child

    def child_count(self):
        return len(self.data)


class LeafProxy(object):
    def __init__(self, key, click_target, data, parent=None):
        self.data = data
        self.parent = parent
        self.key = key
        self.click_target = click_target

    def hasChild(self, row):
        return False

    def childAt(self, row):
        raise Exception("No child")

    def child_count(self):
        return 0

class DictModel(QAbstractItemModel):
    def __init__(self, data, parent=None):
        super(DictModel, self).__init__(parent)

        self.data = data
        self.rootItem = DictProxy('', data)

    def index(self, row, column, parentIndex):
        if not self.hasIndex(row, column, parentIndex):
            return QModelIndex()

        if not parentIndex.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parentIndex.internalPointer()

        if parentItem.hasChild(row):
            return self.createIndex(row, column, parentItem.childAt(row))
        else:
            return QModelIndex()

    def parent(self, childIndex):
        if not childIndex.isValid():
            return QModelIndex()

        childItem = childIndex.internalPointer()
        if childItem.parent is not None:
            return self.createIndex(childItem.parent.row, 0, childItem.parent)
        else:
            return QModelIndex()

    def columnCount(self, parent):
        return 2

    def rowCount(self, parentIndex):
        if parentIndex.column() > 0:
            return 0

        if not parentIndex.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parentIndex.internalPointer()
        return parentItem.childCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        if index.column() == 0:
            return item.key
        else:
            return item.data


class ListModel(QAbstractItemModel):
    def __init__(self, data, parent=None):
        super(ListModel, self).__init__(parent)

        self.data = data
        self.root_item = ListProxy('', data, data)

    def index(self, row, column, parent_index):
        if not self.hasIndex(row, column, parent_index):
            return QModelIndex()

        if not parent_index.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent_index.internalPointer()

        if parent_item.has_child(row):
            return self.createIndex(row, column, parent_item.child_at(row))
        else:
            return QModelIndex()

    def parent(self, child_index):
        if not child_index.isValid():
            return QModelIndex()

        child_item = child_index.internalPointer()
        if child_item.parent is not None:
            return self.createIndex(child_item.parent.row,
                                    0,
                                    child_item.parent)
        else:
            return QModelIndex()

    def columnCount(self, parent):
        return 2

    def rowCount(self, parent_index):
        if parent_index.column() > 0:
            return 0

        if not parent_index.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent_index.internalPointer()
        return parent_item.child_count()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        if index.column() == 0:
            return item.key
        else:
            return item.data



class DictTreeView(object):
    def __init__(self, data):
        self.data = data
        self.treeView = QTreeView()
        self.treeView.setModel(DictModel(self.data))

    def set_on_clicked(self, callback):
        def execute(index):
            callback(index.internalPointer().data)

        self.treeView.clicked.connect(execute)


class NestedListTreeView(object):
    def __init__(self, data):
        self.treeView = QTreeView()
        self.set_data(data)

    def set_on_clicked(self, callback):
        def execute(index):
            callback(index.internalPointer().click_target)

        self.treeView.clicked.connect(execute)

    def set_data(self, data):
        self.data = data
        self.treeView.setModel(ListModel(self.data))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        model_data = collections.OrderedDict([('a', 1),
                                              ('b', 2),
                                              ('c', collections.OrderedDict([('apple', 'red'),
                                                                             ('banana', 'yellow')])),
                                              ('d', collections.OrderedDict([('x', 4),
                                                                             ('y', 5)]))])

        self.model = DictModel(model_data)

        self.view = QTreeView(self)
        self.view.setModel(self.model)

        self.setCentralWidget(self.view)
        self.setWindowTitle("Main Window")
