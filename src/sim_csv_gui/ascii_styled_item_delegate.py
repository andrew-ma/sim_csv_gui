from PyQt5.QtWidgets import QStyle, QStyledItemDelegate
# from PyQt5.QtWidgets import QStyleOptionViewItem
# from PyQt5.QtGui import QPainter
# from PyQt5.QtCore import QModelIndex

class AsciiStyledItemDelegate(QStyledItemDelegate):
    def __init__(self, style: QStyle, parent=None):
        super().__init__(parent)
        self.style = style

    @staticmethod
    def convert_hex_to_ascii(hex_value: str):
        return bytes.fromhex(hex_value).decode("ascii", errors="replace")

    ## Since we are using setItemDelegateForColumn() to choose our columns, then just convert
    def displayText(self, value, locale):
        return AsciiStyledItemDelegate.convert_hex_to_ascii(value)
        
        # return super().displayText(value, locale)

    ## If we are using setItemDelegate(), then we can paint different text for different indexes
    # def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
    #     field_value_column_idx = 1
    #     value_on_card_column_idx = 2

    #     if index.column() in (field_value_column_idx, value_on_card_column_idx):
    #         # paint as ascii
    #         itemOption = QStyleOptionViewItem(option)
    #         self.initStyleOption(itemOption, index)
    #         itemOption.text = AsciiStyledItemDelegate.convert_hex_to_ascii(itemOption.text)
    #         self.style.drawControl(QStyle.ControlElement.CE_ItemViewItem, itemOption, painter, None)
    #     else:
    #         super().paint(painter, option, index)