from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QApplication, QTableView


class ButtonDelegate(QtWidgets.QItemDelegate):
    """
    A delegate that places a fully functioning QButton cell of the column to which it's applied.
    """
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self._pressed = None

    def createEditor(self, parent, option, index):
        """
        Important, otherwise an editor is created if the user clicks in this cell.
        """
        return None

    def paint(self, painter, option, index):
        """
        Paint a checkbox without the label.
        """
        painter.save()
        opt = QtWidgets.QStyleOptionButton()
        opt.text = str(index.data())
        opt.rect = option.rect
        opt.palette = option.palette
        if self._pressed and self._pressed == (index.row(), index.column()):
            opt.state = QtWidgets.QStyle.State_Enabled | QtWidgets.QStyle.State_Sunken
        else:
            opt.state = QtWidgets.QStyle.State_Enabled | QtWidgets.QStyle.State_Raised
        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_PushButton, opt, painter)
        painter.restore()
        
    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model when the button is clicked
        if the user presses the left mousebutton and this button is enabled. Otherwise do nothing.
        '''
        if event.type() == QtCore.QEvent.MouseButtonPress:
            # store the position that is clicked
            self._pressed = (index.row(), index.column())
            return True
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if self._pressed == (index.row(), index.column()):
                # we are at the same place, so emit
                #self.buttonClicked.emit(*self._pressed)
                self.setModelData(None, model, index)
            elif self._pressed:
                # different place.
                # force a repaint on the pressed cell by emitting a dataChanged
                # Note: This is probably not the best idea
                # but I've yet to find a better solution.
                oldIndex = index.model().index(*self._pressed)
                self._pressed = None
                index.model().dataChanged.emit(oldIndex, oldIndex)
            self._pressed = None
            return True
        else:
            # for all other cases, default action will be fine
            return super(ButtonDelegate, self).editorEvent(event, model, option, index)

    def setModelData (self, editor, model, index):
        '''
        The user wanted to change the old state in the opposite.
        '''
        #model.setData(index, 1 if int(index.data()) == 0 else 0, QtCore.Qt.EditRole)
        print('Clicked button at column {}, row {}'.format(index.column(), index.row()))



if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    model = QStandardItemModel(4, 3)
    tableView = QTableView()
    tableView.setModel(model)

    delegate = ButtonDelegate(None)
    tableView.setItemDelegateForColumn(1, delegate)
    for row in range(4):
        for column in range(3):
            index = model.index(row, column, QModelIndex())
            model.setData(index, 1)

    tableView.setWindowTitle("Button Delegate")
    tableView.show()
    sys.exit(app.exec_())