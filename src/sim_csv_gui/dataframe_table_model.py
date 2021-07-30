"""DataframeTableModel
uses Pandas dataframe as the underlying data storage
and the model can be displayed in a table using tableView.setModel(model)
"""
import logging
from PyQt5.QtCore import (
    QVariant,
    Qt,
    QModelIndex,
    QAbstractTableModel,
)

from sim_csv_script.app import check_that_fields_are_valid, check_that_field_is_valid

log = logging.getLogger(__name__)


class DataframeTableModel(QAbstractTableModel):
    def __init__(self, dataframe, parent=None):
        super().__init__(parent)
        self.dataframe = dataframe
        self.editable_column_indexes = (1, 2)
        self.no_save_editable_column_indexes = (2,)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.dataframe.index)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.dataframe.columns)

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            return QVariant(self.dataframe.iloc[index.row(), index.column()])

        if role == Qt.EditRole:
            return QVariant(self.dataframe.iloc[index.row(), index.column()])

    def headerData(
        self, column_index: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.dataframe.columns[column_index])

    def flags(self, index: QModelIndex):
        if index.column() in self.editable_column_indexes:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled
        else:
            return Qt.ItemIsEnabled

    def setData(self, index, value, role=Qt.EditRole):
        row = index.row()
        column = index.column()
        current_value = self.dataframe.iloc[row, column]
        if current_value == value:
            return False
        elif column in self.no_save_editable_column_indexes:
            return False

        # Get a copy of current row
        current_row_series = self.dataframe.iloc[row].copy(deep=True)
        # Set FieldValue in copy to new pending value
        current_row_series["FieldValue"] = value
        try:
            # check if new pending value is valid
            check_that_field_is_valid(
                current_row_series["FieldName"], current_row_series["FieldValue"]
            )
        except Exception as e:
            log.error(f"({e.__class__.__name__}) {e}")
            return False

        # Update the dataframe with the new value
        self.dataframe.iloc[row, column] = value
        return True

    def updateModel(self, dataframe):
        self.beginResetModel()
        self.dataframe = dataframe
        self.endResetModel()

        return self

    def getDataframe(self):
        """Get a copy of the dataframe"""
        return self.dataframe.copy()

    def clear(self):
        self.beginResetModel()
        self.dataframe = pd.DataFrame()
        self.endResetModel()
