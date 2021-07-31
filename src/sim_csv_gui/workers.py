import logging
from PyQt5.QtCore import (
    QMutex,
    QObject,
    pyqtSignal,
)

from sim_csv_script.app import (
    check_pin_adm,
    read_fieldname_simple,
    write_fieldname_simple,
    set_commands_cla_byte_and_sel_ctrl,
    get_card,
    read_card_initial_data,
    verify_full_field_width,
)

log = logging.getLogger(__name__)


class WaitForSIMCardWorker(QObject):
    finished = pyqtSignal(int)
    progress = pyqtSignal(int)

    def __init__(self, sl, parent=None):
        super(WaitForSIMCardWorker, self).__init__(parent)
        self._sl = sl
        self._mutex = QMutex()
        self._running = True
        self._finish_code = 0

    def is_running(self):
        # If variable is currently being modified, then it will be locked
        # we try to lock it, and if it is currently locked, this call will block until it is unlocked (and can be changed)

        self._mutex.lock()
        running = self._running
        self._mutex.unlock()
        return running

    def run(self):
        log.debug("Running WaitForSIMCardWorker run() function")
        while self.is_running():
            try:
                # Every second, stop to check if we are still running
                self._sl.wait_for_card(timeout=1, newcardonly=True)
            except Exception as e:
                pass
            else:
                # If no exception, stop running
                self._mutex.lock()
                self._running = False
                self._mutex.unlock()

        self.finished.emit(self._finish_code)

    def stop(self):
        self._mutex.lock()
        self._running = False
        self._finish_code = 1
        self._mutex.unlock()


class ReadCardWorker(QObject):
    finished = pyqtSignal(int, object)
    progress = pyqtSignal(int)
    read_iccid_and_imsi = pyqtSignal(str, str)

    def __init__(self, df, scc, sl, parent=None):
        super(ReadCardWorker, self).__init__(parent)
        self._df = df
        self._scc = scc
        self._sl = sl
        self._finish_code = 0

    def read_each_field(self, card, row):
        num_fields = len(self._df.index)

        percent_completed = int(((row.name + 1) / num_fields) * 100)
        self.progress.emit(percent_completed)

        return read_fieldname_simple(
            card,
            row["FieldName"],
        )

    def run(self):
        log.debug("Running ReadCardWorker run() function")

        set_commands_cla_byte_and_sel_ctrl(self._scc, self._sl)

        # Default to both Usim and Isim card
        # and it will raise an error if it can't read or write certain fields
        card = get_card("auto", self._scc)

        iccid, imsi = read_card_initial_data(card)
        # Update the iccid and imsi labels
        self.read_iccid_and_imsi.emit(iccid, imsi)

        # For each FieldName, FieldValue pair, write the value
        self._df["Value On Card"] = self._df.apply(
            lambda row: self.read_each_field(card, row),
            axis=1,
        )

        # Create a "Diff" column with differences (case insensitive) between what we passed in, and what we read on card after writing
        differences = self._df["FieldValue"].str.lower() != self._df["Value On Card"].str.lower()
        self._df["Diff"] = differences.apply(lambda b: "X" if b else "")

        self.finished.emit(self._finish_code, self._df)


class WriteCardWorker(QObject):
    finished = pyqtSignal(int, object)
    progress = pyqtSignal(int)
    read_iccid_and_imsi = pyqtSignal(str, str)

    def __init__(
        self,
        df,
        scc,
        sl,
        pin_adm=None,
        imsi_to_pin_dict=None,
        dry_run=True,
        parent=None,
    ):
        super(WriteCardWorker, self).__init__(parent)
        self._df = df
        self._scc = scc
        self._sl = sl
        self._finish_code = 0

        self._pin_adm = pin_adm
        self._imsi_to_pin_dict = imsi_to_pin_dict

        self._dry_run = dry_run

    def write_each_field(self, card, row):
        num_fields = len(self._df.index)

        percent_completed = int(((row.name + 1) / num_fields) * 100)
        self.progress.emit(percent_completed)

        read_value_after_write = write_fieldname_simple(
            card,
            row["FieldName"],
            row["FieldValue"],
            dry_run=self._dry_run,
        )

        # Update ICCID and IMSI labels to new written values
        if row["FieldName"] == "IMSI":
            self.read_iccid_and_imsi.emit(None, read_value_after_write)
        elif row["FieldName"] == "ICCID":
            self.read_iccid_and_imsi.emit(read_value_after_write, None)

        return read_value_after_write

    def run(self):
        log.debug("Running WriteCardWorker run() function")

        set_commands_cla_byte_and_sel_ctrl(self._scc, self._sl)

        # Default to both Usim and Isim card
        # and it will raise an error if it can't read or write certain fields
        card = get_card("auto", self._scc)

        iccid, imsi = read_card_initial_data(card)
        # Update the iccid and imsi labels
        self.read_iccid_and_imsi.emit(iccid, imsi)

        if self._imsi_to_pin_dict is not None:
            pin_adm = self._imsi_to_pin_dict.get(imsi, None)
            assert pin_adm is not None, f"IMSI {imsi} is not found in PIN ADM JSON file"
        else:
            pin_adm = self._pin_adm
            assert pin_adm is not None, "ADM PIN is None"

        # Checking that FieldValue's length in bytes matches binary size of field (since we want to completely overwrite each field)
        # if we can read the binary size, but it doesn't match FieldValue's length in bytes, then it will raise a ValueError
        # and we alert user to fix the input file

        self._df.apply(
            lambda row: verify_full_field_width(
                card, row["FieldName"], row["FieldValue"]
            ),
            axis=1,
        )

        # Submit the PIN to the sim card
        if not self._dry_run:
            log.debug("Submitting PIN to card before writing values")
            # will raise an InvalidADMPinError if pin is invalid
            check_pin_adm(card, pin_adm)

        # For each FieldName, FieldValue pair, write the value to the SIM card
        # "Value On Card" column are values that were read from card after writing
        self._df["Value On Card"] = self._df.apply(
            lambda row: self.write_each_field(card, row),
            axis=1,
        )

        # Create a "Diff" column with differences (case insensitive) between what we passed in, and what we read on card after writing
        differences = self._df["FieldValue"].str.lower() != self._df["Value On Card"].str.lower()
        self._df["Diff"] = differences.apply(lambda b: "X" if b else "")

        self.finished.emit(self._finish_code, self._df)
