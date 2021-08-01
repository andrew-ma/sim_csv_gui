from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
)


def newMesssageBox(
    text,
    *,
    informative_text=None,
    window_title=None,
    icon=QMessageBox.Information,
    buttons=None,
    default_button=None,
    reject_slot=None,
    accept_slot=None,
    finished_slot=None,
    parent=None,
):
    # Returns the QMessageBox
    msg_box = QMessageBox(parent=parent)
    msg_box.setIcon(icon)
    msg_box.setText(text)

    if buttons is not None:
        msg_box.setStandardButtons(buttons)
    if default_button is not None:
        msg_box.setDefaultButton(default_button)
    if informative_text is not None:
        msg_box.setInformativeText(informative_text)
    if window_title is not None:
        msg_box.setWindowTitle(window_title)
    else:
        msg_box.setWindowTitle(window_title)

    if reject_slot is not None:
        msg_box.rejected.connect(reject_slot)

    if accept_slot is not None:
        msg_box.accepted.connect(accept_slot)

    if finished_slot is not None:
        msg_box.finished.connect(finished_slot)

    return msg_box


def openFileDialog(name_filter="*.txt"):
    dlg = QFileDialog()
    dlg.setFileMode(QFileDialog.ExistingFile)
    dlg.setFilter(QDir.Files)
    dlg.setNameFilter(name_filter)

    if dlg.exec_():
        filename = dlg.selectedFiles()[0]
    else:
        filename = None

    return filename
