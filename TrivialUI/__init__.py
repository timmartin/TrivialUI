from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtWidgets import (QMainWindow, QTreeView, QWidget, QPushButton,
                             QFormLayout, QLineEdit, QLabel, QAction)
import collections
import itertools


class GenericProxy(object):
    """The proxy object makes a single piece of Python data navigable in a
    tree context. This is the base class that uses Template Method to
    allow various different sorts of Python data to be navigated in
    this way.

    """

    def __init__(self, data, children, parent=None, row=0):
        assert children is not None

        self.data = data
        self.children = children
        self.parent = parent
        self.row = row
        self.child_cache = {}

    def hasChild(self, row):
        """Check whether this dict has an entry for the specified row. In
        fact, this just checks whether the number of entries in the
        collection is sufficient.
        """

        return row < len(self.children)

    def childCount(self):
        return len(self.children)

    def childAt(self, row):
        if row in self.child_cache:
            return self.child_cache[row]
        else:
            child = self.makeChild(row)
            self.child_cache[row] = child
            return child


class DictProxy(GenericProxy):
    """Proxy object for making a dict of dicts navigable in a form
    usable by PyQt.

    This gives nondeterministic ordering, unless you use an
    OrderedDict.
    """

    def makeChild(self, row):
        items = list(self.children.items())
        key, childItem = items[row]
        if isinstance(childItem, dict):
            return DictProxy(key, childItem, self, row)
        else:
            return LeafProxy(key, None, childItem, self)


class ListProxy(GenericProxy):
    def makeChild(self, row):
        def is_child_list(x): return isinstance(x, list)

        child_lists = list(filter(is_child_list, self.children[row]))
        display_items = list(itertools.filterfalse(is_child_list, self.children[row]))

        if child_lists:
            return ListProxy(display_items, child_lists[0], self)
        else:
            return LeafProxy(self.children[row],
                             self.children[row],
                             self.children[row],
                             self)


class LeafProxy(object):
    def __init__(self, key, click_target, data, parent=None):
        """
        :param key:  The key that identifies this leaf as an
                     entry in the parent data.
        """
        self.data = data
        self.parent = parent
        self.key = key
        self.click_target = click_target

    def hasChild(self, row):
        return False

    def childAt(self, row):
        raise Exception("No child")

    def childCount(self):
        return 0


class GenericModel(QAbstractItemModel):
    def __init__(self, header=None):
        super(GenericModel, self).__init__(None)

        self.header = header

    def index(self, row, column, parentIndex):
        if not self.hasIndex(row, column, parentIndex):
            return QModelIndex()

        if not parentIndex.isValid():
            parentItem = self.root_item
        else:
            parentItem = parentIndex.internalPointer()

        if parentItem.hasChild(row):
            return self.createIndex(row, column, parentItem.childAt(row))
        else:
            return QModelIndex()

    def rowCount(self, parent_index):
        if parent_index.column() > 0:
            return 0

        if not parent_index.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent_index.internalPointer()
        return parent_item.childCount()

    def parent(self, childIndex):
        if not childIndex.isValid():
            return QModelIndex()

        childItem = childIndex.internalPointer()
        if childItem.parent is not None:
            return self.createIndex(childItem.parent.row, 0, childItem.parent)
        else:
            return QModelIndex()

    def data(self, index, role):
        """
        Implementation of a pure virtual base function from Qt.
        """
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        try:
            if item.data[index.column()] is None:
                return ""
            else:
                return str(item.data[index.column()])
        except IndexError as e:
            return ""

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if self.header and len(self.header) >= section + 1:
            return self.header[section]
        else:
            return str(section)


class DictModel(GenericModel):
    def __init__(self, data):
        super(DictModel, self).__init__()

        self.data = data
        self.root_item = DictProxy(None, data)

    def columnCount(self, parent):
        return 2


class ListModel(GenericModel):
    """A model object that exposes the model interface that Qt expects,
    based on a bunch of data provided as (possibly nested) Python list
    objects.

    The tree structure itself is built up inside of the ListProxy
    object stored as self.root_item. The tree is constructed on the
    fly as Qt queries using the index() method.

    """

    def __init__(self, data, header=None):
        """
        :param header:  A list of items that should be displayed
                        as the header labels for the columns.
        """

        super(ListModel, self).__init__(header)

        self.root_item = ListProxy([], data)
        self.num_columns = self._find_num_columns(self.root_item)

    def _find_num_columns(self, data):
        """
        Find the number of columns to use to display this data.
        """
        if isinstance(data, LeafProxy):
            try:
                return len(data.data)
            except AttributeError:
                return 1
        elif isinstance(data, ListProxy) and data.childCount():
            return max(self._find_num_columns(data.childAt(i))
                       for i in range(data.childCount()))
        else:
            return 1

    def columnCount(self, parent):
        return self.num_columns


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
    def __init__(self, data, header=None):
        self.treeView = QTreeView()
        self.header = header
        self.model = None
        self.set_data(data)

        # Expand the root item. I'm not sure if this is a good idea in
        # general, but it works well on some examples. Maybe a
        # heuristic is needed.
        root_index = self.model.index(0, 0, QModelIndex())
        self.treeView.setExpanded(root_index, True)

        # Size all the columns to the size of their current
        # contents. Note that this ignores contents for values in the
        # tree that are collapsed by default, so it's of limited
        # use. However, it's better than the default sizing.
        for i in range(self.model.columnCount(None)):
            self.treeView.resizeColumnToContents(i)

    def set_on_clicked(self, callback):
        def execute(index):
            callback(index.internalPointer().data)

        self.treeView.clicked.connect(execute)

    def set_data(self, data):
        self.data = data
        self.model = ListModel(self.data, header=self.header)
        self.treeView.setModel(self.model)

    def refresh_data(self):
        """Refresh the UI's view of all data in the tree view.  This may be
        inefficient with very large data sets.

        """
        root_index = self.model.index(0, 0, QModelIndex())
        self.treeView.dataChanged(root_index, root_index)


class MainWindow(QMainWindow):
    def __init__(self, menus=None):
        super(MainWindow, self).__init__()

        self.menus = {}
        self.create_default_actions()
        self.create_default_menus()

        if menus:
            for section, menu in menus.items():
                self.menus[section] = self.menuBar().addMenu(section)
                for entry, callback in menu.items():
                    action = QAction(entry, self, triggered=callback)
                    self.menus[section].addAction(action)

    def create_default_actions(self):
        self.exit_action = QAction("E&xit", self,
                                   statusTip="Exit the application",
                                   triggered=self.close)

    def create_default_menus(self):
        self.menus['&File'] = self.menuBar().addMenu('&File')
        self.menus['&File'].addAction(self.exit_action)


class FormWidget(QWidget):
    def __init__(self, parent=None, submit_callback=None, inputs=None):
        super(FormWidget, self).__init__(parent)

        if inputs is None:
            inputs = {}

        self.submit_callback = submit_callback

        self.form = QFormLayout()

        self.inputs = {}
        for key in inputs:
            self.inputs[key] = QLineEdit()
            self.form.addRow(QLabel(key), self.inputs[key])

        self.submitButton = QPushButton("Submit")
        self.submitButton.clicked.connect(self.button_pushed)

        self.form.addRow(self.submitButton)

        self.setLayout(self.form)

    def button_pushed(self, checked):
        if self.submit_callback:
            values = {key: self.inputs[key].text()
                      for key in self.inputs}
            self.submit_callback(values)
