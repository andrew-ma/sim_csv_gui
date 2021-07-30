import argparse
import sys
import logging
import shlex
from PyQt5.QtWidgets import (
    QHeaderView,
    QMainWindow,
    QApplication,
    QMessageBox,
    QFrame,
)
from PyQt5.QtCore import (
    Qt,
    QThread,
)
from PyQt5 import QtGui


log = logging.getLogger(__name__)

from sim_csv_gui.ui_mainwindow import Ui_MainWindow
from sim_csv_gui.temp_settings import TempSettings
from sim_csv_gui.dataframe_table_model import DataframeTableModel
from sim_csv_gui.dialog_boxes import newMesssageBox, openFileDialog
from sim_csv_gui.workers import WaitForSIMCardWorker, ReadCardWorker, WriteCardWorker

from sim_csv_script.app import (
    argparse_add_reader_args,
    initialize_card_reader_and_commands,
    get_dataframe_from_csv,
    check_that_fields_are_valid,
    run_filter_command_on_csv_bytes,
    check_for_added_fields_after_filter,
    JSONFileArgType,
    is_valid_hex,
)


def get_card_reader_args():
    """Even though GUI doesn't use argparse
    The pysim library function uses it configure the Card Reader settings
    And we set using PC/SC reader as the default since we can't provide a CLI arg
    """
    parser = argparse.ArgumentParser()
    parser = argparse_add_reader_args(parser)

    # use PC/SC reader as default
    parser.set_defaults(pcsc_dev=0)
    args = parser.parse_args()
    return args


def setup_logging_basic_config():
    LOG_FORMAT = "[%(levelname)s] %(message)s, line %(lineno)d, function %(funcName)s"

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler()],
    )


class SIM_CSV_GUI:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")

        self.MainWindow = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)

        self.connect_signals_with_slots()
        self.MainWindow.show()

        self.default_palettes = {}
        self.window_title = "SIM CSV GUI"

        self.selected_CSV_filename = None
        self.selected_ADM_PIN_JSON_filename = None

        self.table_model = None
        self.ascii_table_model = None

        self.dry_run = False

        self.settings = TempSettings()

    def run(self):
        setup_logging_basic_config()
        self.set_ui_defaults()

        return self.app.exec_()

    ########################################
    ############### GUI ELEMENTS ###########
    ########################################

    def set_ui_defaults(self):
        # ADM PIN file is disabled
        self.ui.admPinFileInpuContainer.setDisabled(True)
        self.look_disabled(self.ui.admPinFileRadioButton)

        # filter command is disabled
        self.ui.filterCommandLineEdit.setDisabled(True)
        self.look_disabled(self.ui.filterCheckbox)
        self.ui.filterApplyButton.setDisabled(True)

        # Can not show ascii view if no Table model, so disable it
        self.ui.viewAsciiCheckbox.setCheckable(False)

        # table
        self.auto_resize_table()

        self.ui.tableView.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.ui.tableView.show()

        # Progress bar is initially hidden
        self.setup_progress_bar()
        self.ui.readWriteProgressBar.setVisible(False)

        # IMSI and ICCID labels selectable
        self.ui.imsiValue.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.ui.iccidValue.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.ui.imsiContainer.setFrameShape(QFrame.Panel)
        self.ui.imsiContainer.setFrameShadow(QFrame.Sunken)
        self.ui.imsiContainer.setLineWidth(1)
        self.ui.iccidContainer.setFrameShape(QFrame.Panel)
        self.ui.iccidContainer.setFrameShadow(QFrame.Sunken)
        self.ui.iccidContainer.setLineWidth(1)

        # Filenames selectable
        self.ui.dataFilenameLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.ui.admPinFileFilenameLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

    def look_disabled(self, widget):
        palette = widget.palette()

        widget_name = widget.objectName()
        if widget_name not in self.default_palettes:
            self.default_palettes[widget_name] = widget.palette()

        palette.setCurrentColorGroup(QtGui.QPalette.Disabled)
        palette.setColorGroup(
            QtGui.QPalette.Normal,
            palette.windowText(),
            palette.button(),
            palette.light(),
            palette.dark(),
            palette.mid(),
            palette.text(),
            palette.brightText(),
            palette.base(),
            palette.window(),
        )
        palette.setColorGroup(
            QtGui.QPalette.Inactive,
            palette.windowText(),
            palette.button(),
            palette.light(),
            palette.dark(),
            palette.mid(),
            palette.text(),
            palette.brightText(),
            palette.base(),
            palette.window(),
        )

        widget.setPalette(palette)

    def look_normal(self, widget):
        widget_name = widget.objectName()
        if widget_name not in self.default_palettes:
            self.default_palettes[widget_name] = widget.palette()
            return

        widget.setPalette(self.default_palettes[widget_name])

    def disable_input_elements(self):
        # Disable all elements except for table, so user can review the values but not change the inputs
        self.ui.dataGroup.setDisabled(True)
        self.ui.writeGroup.setDisabled(True)
        self.ui.filterGroup.setDisabled(True)
        self.ui.readWriteGroup.setDisabled(True)
        self.ui.viewAsciiCheckbox.setDisabled(True)

    def enable_input_elements(self):
        self.ui.dataGroup.setDisabled(False)
        self.ui.writeGroup.setDisabled(False)
        self.ui.filterGroup.setDisabled(False)
        self.ui.readWriteGroup.setDisabled(False)
        self.ui.viewAsciiCheckbox.setDisabled(False)

    def setup_progress_bar(self):
        self.ui.readWriteProgressBar.reset()
        self.ui.readWriteProgressBar.setMinimum(0)
        self.ui.readWriteProgressBar.setMaximum(100)

    ########################################
    ######### TABLE & DATAFRAME MODEL ######
    ########################################

    def auto_resize_table(self):
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        num_sections = self.ui.tableView.horizontalHeader().count()

        if num_sections >= 4:
            # Resize the Diff column to not stretch
            self.ui.tableView.horizontalHeader().setSectionResizeMode(
                3, QHeaderView.ResizeToContents
            )

        if num_sections >= 1:
            # Resize the FieldName column to fix its contents, to have more room for field values
            self.ui.tableView.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeToContents
            )

        # Save stretched section sizes, so after we change to Interactive for dragging, we start out with saved stretched sizes
        section_sizes = [
            self.ui.tableView.horizontalHeader().sectionSize(i)
            for i in range(num_sections)
        ]

        # Change to Interactive Mode (so user can adjust column width by dragging)
        self.ui.tableView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )

        for i in range(num_sections):
            self.ui.tableView.horizontalHeader().resizeSection(i, section_sizes[i])

    def update_ascii_table(self, dataframe):
        # # update the ASCII Table Model
        # if self.ascii_table_model:
        #     self.ascii_table_model = self.ascii_table_model.updateModel(dataframe)
        # else:
        #     self.ascii_table_model = self.populate_table_using_dataframe(dataframe)

        # self.auto_resize_table()
        # TODO:
        pass

    def update_table(self, dataframe):
        """Create a new DataframeTableModel if one does not currently exist
        Otherwise, update the existing DataframeTableModel
        """
        # update the Table Model without checking if fields are valid
        # can manually check by calling: check_that_fields_are_valid(df)

        table_df = self.get_table_model_dataframe()
        if table_df is not None:
            # Table View already has a DataframeTableModel already exists,
            # So replace its underlying dataframe
            self.ui.tableView.model().updateModel(dataframe)
        else:
            # Table View does not have a DataframeTableModel
            # So create a new Model
            self.populate_table_using_dataframe(dataframe)

        # # enable ascii mode
        # self.ui.viewAsciiCheckbox.setCheckable(True)

        # Resize the table to fit the new dataframe
        self.auto_resize_table()

    def get_table_model_dataframe(self):
        """If Table View's Model is valid, then return its underlying 'dataframe' attribute
        Otherwise return None
        """
        table_model = self.ui.tableView.model()
        if table_model is not None:
            return table_model.dataframe

        return None

    def populate_table_using_dataframe(self, dataframe):
        """Populates Qt table using dataframe

        Each time, this creates a new model, and sets the table View to use this new model

        so only call this function when importing a new CSV file

        for existing CSV file, to update the current model, use the 'update_table(self, dataframe)' function instead
        """
        # Create a new Dataframe Model
        model = DataframeTableModel(dataframe)

        # And display it in the Table View
        self.ui.tableView.setModel(model)

        # Not returning anything, because we can access the model object through tableView.model()

    ########################################
    ############ FILTER COMMAND ############
    ########################################

    def get_filter_command(self):
        """Read the filter command from the filter text box"""
        assert self.ui.filterCheckbox.isChecked()

        filter_text = self.ui.filterCommandLineEdit.text().strip()

        if not filter_text:
            raise Exception("Filter command is empty.")

        # FILTER COMMAND
        filter_command = shlex.split(filter_text)
        log.debug(f"My Filter: {repr(filter_command)}")
        return filter_command

    @staticmethod
    def filter_dataframe(df, filter_command):
        """This takes in an existing dataframe and runs it through the filter command
        It then returns a new dataframe object
        It also checks for any newly added fields

        Args:
            df ([type]): [description]
            filter_command ([type]): [description]

        Returns:
            [type]: [description]
        """
        previous_field_names = df["FieldName"].to_list()

        # Convert dataframe to bytes
        df_bytes = df.to_csv().encode()

        df = run_filter_command_on_csv_bytes(df_bytes, filter_command)

        after_filter_field_names = df["FieldName"].to_list()
        check_for_added_fields_after_filter(
            previous_field_names, after_filter_field_names
        )

        return df

    ########################################
    ############ SIGNALS & SLOTS ###########
    ########################################

    def connect_signals_with_slots(self):
        # Data
        self.ui.dataChooseFileButton.clicked.connect(
            self.on_dataChooseFileButton_clicked
        )

        # ADM PIN
        self.ui.admPinRadioButton.toggled.connect(self.on_admPinRadioButton_toggled)

        self.ui.admPinHexadecimalCheckbox.stateChanged.connect(
            self.on_admPinHexadecimalCheckbox_stateChanged
        )

        # ADM PIN FILE
        self.ui.admPinFileRadioButton.toggled.connect(
            self.on_admPinFileRadioButton_toggled
        )

        self.ui.admPinFileChooseFileButton.clicked.connect(
            self.on_admPinFileChooseFileButton_clicked
        )

        # Filter
        self.ui.filterCheckbox.stateChanged.connect(self.on_filterCheckbox_stateChanged)
        self.ui.filterApplyButton.clicked.connect(self.on_filterApplyButton_clicked)

        # READ/WRITE BUTTONS
        self.ui.readButton.clicked.connect(self.on_readButton_clicked)
        self.ui.writeButton.clicked.connect(self.on_writeButton_clicked)

        # View ASCII Button
        self.ui.viewAsciiCheckbox.stateChanged.connect(
            self.on_viewAsciiCheckbox_stateChanged
        )

    def on_dataChooseFileButton_clicked(self):
        log.debug("on_dataChooseFileButton_clicked()")

        csv_filename = openFileDialog("*.csv")
        if csv_filename is not None:
            # update the label
            self.ui.dataFilenameLabel.setText(csv_filename)

            # and show in the Qt Table View
            try:
                # Create a new dataframe by reading from CSV file
                df = get_dataframe_from_csv(csv_filename)

                check_that_fields_are_valid(df)
                # if fields in CSV are valid, then display dataframe in Table
                self.update_table(df)

                self.selected_CSV_filename = csv_filename
            except Exception as e:
                # clear the label
                self.ui.dataFilenameLabel.setText("No file selected")
                self.selected_CSV_filename = None

                # Remove table from view
                if self.table_model:
                    self.table_model.clear()
                else:
                    self.table_model = None

                log.error(e)
                self.openErrorDialog(e.__class__.__name__, informative_text=str(e))

    def on_admPinFileRadioButton_toggled(self, checked: bool):
        log.debug("on_admPinFileRadioButton_toggled()")
        if checked:
            self.ui.admPinFileInpuContainer.setDisabled(False)
            self.look_normal(self.ui.admPinFileRadioButton)
        else:
            self.ui.admPinFileInpuContainer.setDisabled(True)
            self.look_disabled(self.ui.admPinFileRadioButton)

    def on_admPinRadioButton_toggled(self, checked: bool):
        log.debug("on_admPinRadioButton_toggled()")
        if checked:
            self.ui.admPinInputContainer.setDisabled(False)
            self.look_normal(self.ui.admPinRadioButton)
        else:
            self.ui.admPinInputContainer.setDisabled(True)
            self.look_disabled(self.ui.admPinRadioButton)

    def on_admPinFileChooseFileButton_clicked(self):
        log.debug("on_admPinFileChooseFileButton_clicked()")
        json_filename = openFileDialog("*.json")
        if json_filename is not None:
            self.ui.admPinFileFilenameLabel.setText(json_filename)

            self.selected_ADM_PIN_JSON_filename = json_filename

    def on_admPinHexadecimalCheckbox_stateChanged(self, state: int):
        log.debug("on_admPinHexadecimalCheckbox_stateChanged()")

        admPin = self.ui.admPinLineEdit.text()
        if state == Qt.Checked:
            # prepend '0x' to the current value in input field
            self.ui.admPinLineEdit.setText("0x" + admPin)
        elif state == Qt.Unchecked:
            if admPin.startswith("0x"):
                admPin = admPin[2:]
            self.ui.admPinLineEdit.setText(admPin)

    def on_filterCheckbox_stateChanged(self, state: int):
        log.debug("on_filterCheckbox_stateChanged()")

        if state == Qt.Checked:
            self.ui.filterCommandLineEdit.setEnabled(True)
            self.look_normal(self.ui.filterCheckbox)
            self.ui.filterApplyButton.setEnabled(True)
        elif state == Qt.Unchecked:
            # Disable the text edit
            self.ui.filterCommandLineEdit.setEnabled(False)
            self.look_disabled(self.ui.filterCheckbox)
            self.ui.filterApplyButton.setEnabled(False)

            #     # TODO:
            # # return the Table to unfiltered form
            # if self.selected_CSV_filename:
            #     # df = get_dataframe_from_csv(self.selected_CSV_filename)
            #     table_df = self.get_table_model_dataframe()

            #     self.update_table(df)

    def on_filterApplyButton_clicked(self):
        log.debug("on_filterApplyButton_clicked()")

        try:
            if not self.selected_CSV_filename:
                raise Exception("Requires CSV file")

            filter_command = self.get_filter_command()
            # df = get_filtered_dataframe(self.selected_CSV_filename, filter_command)
            # TODO: only get new dataframe if it is empty
            table_df = self.get_table_model_dataframe()
            df = self.filter_dataframe(table_df, filter_command)

            check_that_fields_are_valid(df)
            self.update_table(df)

        except Exception as e:
            log.error(e)
            self.openErrorDialog(e.__class__.__name__, informative_text=str(e))

    def on_viewAsciiCheckbox_stateChanged(self, state: int):
        log.debug("on_viewAsciiCheckbox_stateChanged()")

        if state == Qt.Checked:

            ascii_df = self.table_model.getDataframe()

            # Convert values in columns to ascii
            ascii_df["FieldValue"] = ascii_df["FieldValue"].apply(
                lambda value: bytes.fromhex(value).decode("ascii", errors="replace")
            )

            try:
                ascii_df["Value On Card"] = ascii_df["Value On Card"].apply(
                    lambda value: bytes.fromhex(value).decode("ascii", errors="replace")
                )
            except KeyError:
                # KeyError if we haven't read card values yet, and 'Value On Card' column has not been created
                pass

            self.update_ascii_table(ascii_df)

            # Show ascii model in table view
            self.ui.tableView.setModel(self.ascii_table_model)

        elif state == Qt.Unchecked:
            # Show actual model in table view
            self.ui.tableView.setModel(self.table_model)

    def on_readButton_clicked(self):
        log.debug("on_readButton_clicked()")
        self.read_mode()

    def on_writeButton_clicked(self):
        log.debug("on_writeButton_clicked()")
        self.write_mode()

    def set_progress_bar_value(self, value):
        self.ui.readWriteProgressBar.setValue(value)

    def update_iccid_and_imsi_labels(self, iccid=None, imsi=None):
        if iccid is not None:
            self.ui.iccidValue.setText(iccid)

        if imsi is not None:
            self.ui.imsiValue.setText(imsi)

    ########################################
    ########### DIALOG BOXES ###############
    ########################################


    def save_dialog_position(self, dialog):
        self.settings.setValue("last_pos", dialog.pos())
        self.settings.sync()

    def restore_dialog_position(self, dialog):
        last_pos = self.settings.value("last_pos")
        if last_pos is not None:
            dialog.move(last_pos)

    def openNonModalMessageBox(self, text, *args, **kwargs):
        non_modal_msg_box = newMesssageBox(
            text,
            parent=self.MainWindow,
            window_title=self.window_title,
            *args,
            **kwargs,
        )
        non_modal_msg_box.setModal(False)

        self.restore_dialog_position(non_modal_msg_box)
        non_modal_msg_box.finished.connect(
            lambda: self.save_dialog_position(non_modal_msg_box)
        )

        non_modal_msg_box.show()
        return non_modal_msg_box

    def openMessageBox(self, text, *args, **kwargs):
        modal_msg_box = newMesssageBox(
            text,
            parent=self.MainWindow,
            window_title=self.window_title,
            *args,
            **kwargs,
        )

        # Save to instance variables, so other methods can close box
        self.modal_msg_box = modal_msg_box

        modal_msg_box.exec_()
        return modal_msg_box

    def openErrorDialog(self, text, *args, **kwargs):
        return self.openMessageBox(text, icon=QMessageBox.Critical, *args, **kwargs)

    def openInsertSimMessageBox(self, *args, **kwargs):
        return self.openMessageBox(
            "Insert SIM card...", buttons=QMessageBox.Cancel, *args, **kwargs
        )

    ########################################
    ########### WAIT FOR SIM CARD ##########
    ########################################

    def setup_card_reader_and_wait_for_sim_card(self, callback=None):
        if self.selected_CSV_filename is None:
            raise Exception("CSV File is Required")

        table_df = self.get_table_model_dataframe()

        if self.ui.filterCheckbox.isChecked():
            filter_command = self.get_filter_command()
            df = self.filter_dataframe(table_df, filter_command)
        else:
            # NO FILTER
            # Only Create New Dataframe From CSV file if Table View does not have a Model
            # TODO:
            # df = get_dataframe_from_csv(self.selected_CSV_filename)
            df = table_df

        check_that_fields_are_valid(df)
        self.update_table(df)

        ###############################################
        # Card Reader Stuff
        reader_args = get_card_reader_args()
        log.debug("Initializing Card Reader and Commands")

        sl, scc = initialize_card_reader_and_commands(reader_args)

        # Disable buttons while msg box
        self.disable_input_elements()

        # Wait for SIM card to be inserted in Separate Thread
        self.wait_for_sim_card(sl)

        def __insert_sim_reject_callback():
            log.debug("REJECTED INSERTING SIM CARD")
            try:
                # Depending on if worker is already deleted, when inserted card
                # This will work if we press Cancel button, which will trigger the worker to stop
                self.wait_for_sim_card_worker.stop()
            except Exception:
                pass

        def __insert_sim_accept_callback():
            log.debug("INSERTED SIM CARD")

            # Run read_card, or write_card
            if callback is not None:
                callback(dataframe=df, scc=scc, sl=sl)

        def __insert_sim_finished_callback():
            # Enable Buttons
            self.enable_input_elements()

        log.debug("Opening insert sim message box")
        self.openInsertSimMessageBox(
            reject_slot=__insert_sim_reject_callback,
            accept_slot=__insert_sim_accept_callback,
            finished_slot=__insert_sim_finished_callback,
        )

    def wait_for_sim_card(self, _sl):
        # create a QThread object
        wait_for_sim_card_thread = QThread()

        # create a worker object
        self.wait_for_sim_card_worker = WaitForSIMCardWorker(_sl)

        # Move worker to the thread
        self.wait_for_sim_card_worker.moveToThread(wait_for_sim_card_thread)

        # Connect signals and slots

        # When Thread emits 'started' signal, run the Worker slot function
        wait_for_sim_card_thread.started.connect(self.wait_for_sim_card_worker.run)

        def __worker_finished(finish_code):
            log.debug(f"Wait For SIM Card Worker Finished With {finish_code}")

            if finish_code == 0:
                # Close the Message Box
                self.modal_msg_box.accept()
            else:
                # Don't reject(), just close, since reject will try to stop the Wait For Sim Card Thread
                self.modal_msg_box.done(2)

            self.wait_for_sim_card_worker.deleteLater()
            wait_for_sim_card_thread.quit()

        self.wait_for_sim_card_worker.finished.connect(__worker_finished)

        def __thread_finished():
            wait_for_sim_card_thread.deleteLater()

        wait_for_sim_card_thread.finished.connect(__thread_finished)

        log.debug("Starting thread")
        wait_for_sim_card_thread.start()

    ########################################
    ########### READ SIM CARD ##############
    ########################################

    def read_mode(self):
        # Don't show ascii table
        self.ui.viewAsciiCheckbox.setChecked(False)

        def read_callback(dataframe, scc, sl):
            self.read_card(dataframe=dataframe, scc=scc, sl=sl)

        try:
            self.setup_card_reader_and_wait_for_sim_card(callback=read_callback)
        except Exception as e:
            log.error(e)
            self.openErrorDialog(e.__class__.__name__, informative_text=str(e))

    def read_card(self, dataframe, scc, sl, callback=None):
        """[summary]

        Args:
            dataframe ([type]): [description]
            scc ([type]): [description]
            sl ([type]): [description]
            callback (dataframe, scc, sl): Is called if read worker finishes with finish_code == 0
        """
        # create a QThread object
        read_card_thread = QThread()

        # create a Worker object
        read_card_worker = ReadCardWorker(dataframe, scc, sl)

        # Move worker to the thread
        read_card_worker.moveToThread(read_card_thread)

        # Connect Signals and Slots

        # When Thread emits 'started' signal, run the Worker slot function
        def __run_read_card_worker():
            try:
                read_card_worker.run()
            except Exception as e:
                # Show Error
                self.openErrorDialog(e.__class__.__name__, informative_text=str(e))
                # Emit finished signal, but error, and show unchanged dataframe in table
                read_card_worker.finished.emit(1, None)

        read_card_thread.started.connect(__run_read_card_worker)

        # When Worker emits 'progress' signal, update the progress bar value
        read_card_worker.progress.connect(self.set_progress_bar_value)

        # When Worker reads iccid and imsi, and emits a signal, then we update the labels
        read_card_worker.read_iccid_and_imsi.connect(self.update_iccid_and_imsi_labels)

        def __worker_finished(finish_code, new_dataframe):
            log.debug(f"Read Card Worker Finished With {finish_code}")
            # Enable Buttons before callback is called, because callback might want to Disable buttons
            self.enable_input_elements()

            if finish_code == 0:
                if callback is not None:
                    callback(dataframe=dataframe, scc=scc, sl=sl)

            read_card_worker.deleteLater()
            read_card_thread.quit()

            # Update Table with New Dataframe
            if new_dataframe is not None:
                self.update_table(new_dataframe)

        read_card_worker.finished.connect(__worker_finished)

        def __thread_finished():
            log.debug("Read Card Thread Finished")
            read_card_thread.deleteLater()

        read_card_thread.finished.connect(__thread_finished)

        ########################################################
        # Disable Buttons
        self.disable_input_elements()

        # Reset the progress bar
        self.ui.readWriteProgressBar.setValue(0)
        self.ui.readWriteProgressBar.setVisible(True)

        # Start the Thread
        read_card_thread.start()

    def write_mode(self):
        # Don't show ascii table
        self.ui.viewAsciiCheckbox.setChecked(False)

        try:
            pin_adm, imsi_to_pin_dict = self.get_adm_pin_from_input_fields()

            def read_then_write_callback(dataframe, scc, sl):
                def ask_user_if_write_callback(*args, **kwargs):
                    # finished reading successfully

                    self.disable_input_elements()

                    # Enable showing ascii table on ask to write dialog
                    self.ui.viewAsciiCheckbox.setDisabled(False)

                    def __accept_ask_write_callback():
                        log.debug("Writing SIM Card")
                        # If user accepts write values dialog, show hex values
                        self.ui.viewAsciiCheckbox.setChecked(False)

                        self.write_card(
                            dataframe,
                            scc,
                            sl,
                            pin_adm,
                            imsi_to_pin_dict,
                            dry_run=self.dry_run,
                        )

                    def __finished_ask_write_callback():
                        # Restore disabled elements
                        self.enable_input_elements()

                    self.openNonModalMessageBox(
                        "Write Values?",
                        buttons=QMessageBox.Cancel | QMessageBox.Ok,
                        icon=QMessageBox.Warning,
                        default_button=QMessageBox.Cancel,
                        accept_slot=__accept_ask_write_callback,
                        finished_slot=__finished_ask_write_callback,
                    )

                self.read_card(
                    dataframe=dataframe,
                    scc=scc,
                    sl=sl,
                    callback=ask_user_if_write_callback,
                )

            self.setup_card_reader_and_wait_for_sim_card(
                callback=read_then_write_callback
            )

        except Exception as e:
            log.error(e)
            self.openErrorDialog(e.__class__.__name__, informative_text=str(e))

    def get_adm_pin_from_input_fields(self):
        if self.ui.admPinRadioButton.isChecked():
            # Make sure that the ADM pin is valid
            pin_adm = self.ui.admPinLineEdit.text().strip()
            if not pin_adm:
                raise Exception("ADM PIN is empty")

            if pin_adm.startswith("0x") and not is_valid_hex(pin_adm):
                raise Exception("ADM PIN is not valid hex")
            imsi_to_pin_dict = None
        elif self.ui.admPinFileRadioButton.isChecked():
            # Make sure that a valid file is selected
            if self.selected_ADM_PIN_JSON_filename is None:
                raise Exception("ADM PIN file is empty")

            imsi_to_pin_dict = JSONFileArgType(self.selected_ADM_PIN_JSON_filename)
            pin_adm = None

        return pin_adm, imsi_to_pin_dict

    def write_card(
        self,
        dataframe,
        scc,
        sl,
        pin_adm=None,
        imsi_to_pin_dict=None,
        callback=None,
        dry_run=True,
    ):
        # create a QThread object
        write_card_thread = QThread()

        # create a Worker object
        write_card_worker = WriteCardWorker(
            dataframe, scc, sl, pin_adm, imsi_to_pin_dict, dry_run=dry_run
        )

        # Move worker to the thread
        write_card_worker.moveToThread(write_card_thread)

        # Connect Signals and Slots

        # When Thread emits 'started' signal, run the Worker slot function
        def __run_write_card_worker():
            try:
                write_card_worker.run()
            except Exception as e:
                # Show Error
                self.openErrorDialog(e.__class__.__name__, informative_text=str(e))
                # Emit finished signal, but error, and show unchanged dataframe in table
                write_card_worker.finished.emit(1, None)

        write_card_thread.started.connect(__run_write_card_worker)

        # When Worker emits 'progress' signal, update the progress bar value
        write_card_worker.progress.connect(self.set_progress_bar_value)

        # When Worker reads iccid and imsi, and emits a signal, then we update the labels
        write_card_worker.read_iccid_and_imsi.connect(self.update_iccid_and_imsi_labels)

        def __worker_finished(finish_code, new_dataframe):
            # Enable Buttons before callback is called, because callback might want to Disable buttons
            self.enable_input_elements()

            if finish_code == 0:
                if callback is not None:
                    log.debug("Running write_card() callback function")
                    callback(dataframe=dataframe, scc=scc, sl=sl)
                self.openMessageBox("Write successful!")
            else:
                self.openErrorDialog("Write failed!")

            write_card_worker.deleteLater()
            write_card_thread.quit()

            # Update Table with New Dataframe
            if new_dataframe is not None:
                self.update_table(new_dataframe)

        write_card_worker.finished.connect(__worker_finished)

        def __thread_finished():
            write_card_thread.deleteLater()

        write_card_thread.finished.connect(__thread_finished)

        ########################################################
        # Disable Buttons
        self.disable_input_elements()

        # Reset the progress bar
        self.ui.readWriteProgressBar.setValue(0)
        self.ui.readWriteProgressBar.setVisible(True)

        # Start the Thread
        write_card_thread.start()


def main():
    gui = SIM_CSV_GUI()
    sys.exit(gui.run())


if __name__ == "__main__":
    main()
