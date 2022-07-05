# SIM CSV GUI
GUI desktop application for reading and writing SIM cards values.

![Screenshot of GUI](https://github.com/andrew-ma/sim_csv_gui/blob/main/docs/gui_screenshot.png?raw=true)

* For reading and writing values, import a CSV file with `FieldName,FieldValue` columns

* For writing values, import a JSON file with `{"IMSI": "ADM PIN"}` (ADM PINs are treated as ASCII unless prefixed with "0x" for hexadecimal)

* Values are editable in table, and they can be displayed as ASCII characters 

* An external filter program that receives a CSV valid string  through STDIN, modifies field values, and outputs the modified CSV string through STDOUT can be supplied

## Dependencies (Linux)
```
sudo apt-get install -y swig
sudo apt-get install -y libpcsclite-dev
```


## Installation
### Method #1: Source Distribution (`.tar.gz` file)
Windows
```
python -m pip install --upgrade {sim_csv_script-VERSION.tar.gz}
```

Linux
```
python3 -m pip install --upgrade {sim_csv_script-VERSION.tar.gz}
```

### Method #2: Source Code
* First, change into the directory that contains *`setup.py`* or *`setup.cfg`* file

Windows
```
python -m pip install --upgrade -e .
```

> _Windows_: if you get a "swig.exe" error while running the installation command, you will need to download the swig prebuilt executable (http://www.swig.org/download.html), extract the zip, and add the folder to your PATH.  Try running the installation steps again, and if it fails with a "Visual Studio Build Tools" error, then you will need to download https://visualstudio.microsoft.com/visual-cpp-build-tools/, install it, and select the "Desktop development with C++"


Linux
```
python3 -m pip install --upgrade -e .
```

> _Linux_: if you get a "swig: not found" error while running the installation command, first ensure that Python 3.6 or later is installed (`python3 --version`).  If so, install swig with `sudo apt install swig` and retry the installation command


---
## Commands

Launch GUI
```
sim_csv_gui
```

To list valid field names that can used in the CSV file
```
sim_csv_script --list-field-names
```

---

## For [Development Documentation](docs/development.md)
