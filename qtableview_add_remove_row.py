from PyQt5.QtWidgets import QTableView, QTableWidget, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QStyle, QItemDelegate, QStyleOptionButton
from PyQt5.QtGui import QStandardItemModel, QIcon
from PyQt5.QtCore import QModelIndex, QVariant, Qt, QAbstractTableModel
from random import randint


class Model(QAbstractTableModel):
    def __init__(self, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.data = []

        
    def rowCount(self, parent=QModelIndex()):
        return len(self.data)      

    def columnCount(self, parent=QModelIndex()):
        return 3

    def data(self, index, role):
        if not index.isValid(): return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()

        row = index.row()
        column = index.column()

        if column == 0:
            if row < len(self.data):
                return QVariant(self.data[row]['A'])
        elif column == 1:
            if row < len(self.data):
                return QVariant(self.data[row]['B'])
        elif column == 2:
            if row < len(self.data):
                return QVariant(self.data[row]['C'])
        else:
            return QVariant()
        
    def headerData(self, rowcol, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if rowcol == 0:
                return 'A'
            elif rowcol == 1:
                return 'B'
            elif rowcol == 2:
                return 'C'
        return None

    def removeRow(self, row_index):
        print('removeRow({})'.format(row_index))
        self.beginRemoveRows(QModelIndex(), row_index, row_index)       
        #self.data = self.data[:row_index] + self.data[row_index:]
        del(self.data[row_index])
        self.endRemoveRows()
        return True

    def insertRow(self):
        print('insertRows()')
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        entry = {'A': randint(0, 9), 'B': randint(0, 9), 'C': randint(0, 9)}
        self.data.insert(self.rowCount() + 1, entry)
        self.endInsertRows()
        return True


class MyWindow(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        vLayout = QVBoxLayout(self)
        self.setLayout(vLayout)

        hLayout = QHBoxLayout()
        vLayout.insertLayout(0, hLayout)

        tableModel = Model(self)      

        self.ViewA=QTableView(self)
        self.ViewA.setModel(tableModel)
        self.ViewA.clicked.connect(self.viewClicked)
        self.ViewA.setSelectionBehavior(QTableView.SelectRows)
        self.ViewA.setSelectionMode(QTableWidget.SingleSelection)

        hLayout.addWidget(self.ViewA)

        insertButton = QPushButton('Insert Row Above Selection')
        insertButton.setObjectName('insertButton')
        insertButton.clicked.connect(self.buttonClicked)
        removeButton = QPushButton('Remove Selected Item')
        removeButton.setObjectName('removeButton')
        removeButton.clicked.connect(self.buttonClicked)

        vLayout.addWidget(insertButton)
        vLayout.addWidget(removeButton)

    def getZeroColumnSelectedIndexes(self, tableView=None):
        if not tableView:
            return
        selectedIndexes = tableView.selectedIndexes()
        if not selectedIndexes:
            return
        return [index for index in selectedIndexes if not index.column()]

    def viewClicked(self, indexClicked):
        print('indexClicked() row: {}  column: {}'.format(indexClicked.row(), indexClicked.column()))
        proxy = indexClicked.model()

    def buttonClicked(self):
        button=self.sender()
        if not button:
            return
        
        zeroColumnSelectedIndexes = self.getZeroColumnSelectedIndexes(self.ViewA)
        if button.objectName() == 'removeButton':
            if not zeroColumnSelectedIndexes:
                print('not zeroColumnSelectedIndexes')
                return
            
            firstZeroColumnSelectedIndex = zeroColumnSelectedIndexes[0]
            if not firstZeroColumnSelectedIndex or not firstZeroColumnSelectedIndex.isValid():
                print('buttonClicked(): not firstZeroColumnSelectedIndex.isValid()')
                return
        
            startingRow=firstZeroColumnSelectedIndex.row()
            print('buttonClicked() startingRow = {}'.format(startingRow))
            if button.objectName() == 'removeButton':
                self.ViewA.model().removeRow(startingRow)
                
        elif button.objectName() == 'insertButton':
            self.ViewA.model().insertRow()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())