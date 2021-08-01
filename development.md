# Development

## System Requirements
* Python 3.6 or later ([Python Installation Steps](python-installation.md))

## Python Package Dependencies:
* sim_csv_script @ https://github.com/andrew-ma/sim_csv_script/archive/main.zip
* PyQt5
* pyqt5-tools

## Installation
Windows
```
git clone -b main https://github.com/andrew-ma/sim_csv_gui
cd sim_csv_gui
python -m pip install --upgrade --no-cache-dir -e .
```

Linux
```
git clone -b main https://github.com/andrew-ma/sim_csv_gui
cd sim_csv_gui
python3 -m pip install --upgrade --no-cache-dir -e .
```

---

## Edit User Interface

### Qt Designer - WYSIWYG (what you see is what you get) GUI editor

#### Install Qt Designer
Windows
```
python -m pip install pyqt5-tools
```

Linux
```
python3 -m pip install pyqt5-tools
```

#### Launch Qt Designer
```
pyqt5-tools designer
```

* Open .ui files (src/sim_csv_gui/UI) in Qt Designer to load in current user interface

* After making changes in Qt Designer, regenerate the Python code so the main program can use the modified UI

```
# On Windows, run from the 'src/sim_csv_gui' folder

python generate.py --package-name sim_csv_gui --ui-files UI\ui_mainwindow.ui --resource-files resources\resources.qrc
```
---

## Build Executable Steps (Windows)
View [Building Executable Documentation](build_executable_steps.md)
