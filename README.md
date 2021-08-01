# SIM CSV GUI
Powered by sim_csv_script
GUI to read and write SIM cards.
Fields and values are specified in a CSV file, and optionally a filter script can be supplied for dynamically changing the CSV contents for each card.

## Download Windows Executable
https://github.com/andrew-ma/sim_csv_gui/releases/latest

---
## Download Python Package (for other OS and platforms)
### System Requirements
* Python 3.6 or later ([Python Installation Steps](python_installation_steps.md))


### Installation
> _Windows_: substitute `python3` with `python`
```
# Upgrade pip if using older version of Python
python3 -m pip install --upgrade pip


python3 -m pip install --upgrade --no-cache-dir https://github.com/andrew-ma/sim_csv_gui/archive/main.zip
```
> _Linux_: if you get a "swig: not found" error while running the installation command, first ensure that Python 3.6 or later is installed ('`python3 --version`').  If so, install swig with '`sudo apt install swig`' and retry the installation command.

> _Windows_: if you get a "swig.exe" error while running the installation command, you will need to download the swig prebuilt executable (http://www.swig.org/download.html), extract the zip, and add the folder to your PATH.  Then try running the installation again, and if it fails with a "Visual Studio Build Tools" error, then you will need to download https://visualstudio.microsoft.com/visual-cpp-build-tools/, install it, and select the "Desktop development with C++"


---
## Commands

Launch GUI
```
sim_csv_gui
```

To list valid field names that can used in CSV file
```
sim_csv_script --list-field-names
```

---

## For [Development Documentation](development.md)
