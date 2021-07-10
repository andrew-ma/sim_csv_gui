# Development

## System Requirements
* Python 3.7 or later ([Python Installation Steps](python-installation.md))

## Python Package Dependencies:
* sim_csv_script @ https://github.com/andrew-ma/sim_csv_script/archive/main.zip
* PyQt5
* pyqt5-tools

## Install for Development
```
git clone -b main https://github.com/andrew-ma/sim_csv_gui
cd sim_csv_gui
pip install -e .
```

## Uninstall everything including dependencies
```
pip uninstall sim_csv_gui -y
pip uninstall -r requirements.txt -y
pip uninstall -r requirements_dev.txt -y
```

---

## __GUI Development__
To install Qt Designer
```
pip install -r requirements_dev.txt
```

To launch Qt Designer to modify the UI
```
pyqt5-tools designer
```

Then, you can import the .ui file in Qt Designer to modify the GUI.

After you modify the Qt Designer .ui file, you can regenerate the python code by running (from the 'sim_csv_gui' folder):
```
# Windows
python generate.py --package-name sim_csv_gui --ui-files UI\ui_mainwindow.ui --resource-files resources\resources.qrc
```

To launch the GUI while in development, run (from the 'sim_csv_gui' folder)
```
python3 ui_mainwindow.py
```

The entry point for the gui is the main function in sim_csv_gui/app.py.
