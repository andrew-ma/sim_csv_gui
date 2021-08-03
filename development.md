# Development

## System Requirements
* Python 3.6 or later ([Python Installation Steps](python-installation.md))

## Python Package Dependencies:
* sim_csv_script
* PyQt5
* pyqt5-tools

## Developer Installation
* First, change into the directory that contains *`setup.py`* or *`setup.cfg`* file

Windows
```
python -m pip install --upgrade --no-cache-dir -e .
```

### Modifying Dependencies
* To use modified dependencies (e.g. using your new version of sim_csv_script with bugfixes), we will need to change the *requirements.txt* file to point to your new modified version
  * If modified version is uploaded to PyPi, then simply replace `OLD_PACKAGE` with `NEW_PACKAGE`
  * If modified version is uploaded to a Github repo, then replace `OLD_PACKAGE` with
    ```
    NEW_PACKAGE @ https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/archive/{GITHUB_BRANCH}.zip
    ```
    * e.g. "sim_csv_script @ https://github.com/GITHUB_USERNAME/sim_csv_script/archive/master.zip"
  * Run the [Developer Installation](#developer-installation) command again
    * `--no-cache-dir` will always redownload the latest files

---

## Editing User Interface

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

* Open *.ui* files (*`src/sim_csv_gui/UI/`*) in Qt Designer to load in current user interface

#### Converting Qt Designer User Interface files (*.ui*) and Qt Designer Resource files (*.qrc*) to Python code
* After making changes in Qt Designer, we must regenerate the Python code so the main program can use the modified UI and resources

* First, change into the directory that contains *`setup.py`* or *`setup.cfg`* file

Windows
```
python generate_ui_resource.py --package-name sim_csv_gui --ui-files src/sim_csv_gui/UI/ui_mainwindow.ui --resource-files src/sim_csv_gui/resources/resources.qrc --output-dir src/sim_csv_gui
```

Linux
```
python3 generate_ui_resource.py --package-name sim_csv_gui --ui-files src/sim_csv_gui/UI/ui_mainwindow.ui --resource-files src/sim_csv_gui/resources/resources.qrc --output-dir src/sim_csv_gui
```

---

## Creating Source Distribution (`.tar.gz` file)
* Source distribution file (*`sim_csv_gui*-VERSION.tar.gz`*) will be created in *dist/* folder

Windows
```
make_distribution.bat
```

Linux
```
# TODO: create make_distribution.bat equivalent bash script
```

## Installing Source Distribution (`.tar.gz` file)
Windows
```
python -m pip install {sim_csv_gui-VERSION.tar.gz}
```

Linux
```
python3 -m pip install {sim_csv_gui-VERSION.tar.gz}
```

---
## Creating a Standalone Executable (`.exe` file)
* Standalone executable  will be created in _build_executable/dist/_.

1. Change into the directory that contains *`setup.py`* or *`setup.cfg`* file

2. Download UPX from https://github.com/upx/upx/releases/latest, and extract it.  Set the `UPX_PATH` environment variable to the extracted upx directory.

Windows
```
set "UPX_PATH=upx-3.96-win64"
make_executable.bat
```

Linux
```
# TODO: create make_executable.bat equivalent bash script
```