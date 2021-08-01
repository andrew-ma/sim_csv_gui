# SIM CSV GUI
Powered by sim_csv_script
GUI to read and write SIM cards.
Fields and values are specified in a CSV file, and optionally a filter script can be supplied for dynamically changing the CSV contents for each card.

## Download Prebuilt Binaries
https://github.com/andrew-ma/sim_csv_gui/releases/latest

---
## Download Python Package
### System Requirements
* Python 3.6 or later ([Python Installation Steps](python_installation_steps.md))


### Installation
#### Method #1
Windows
```
set PBR_VERSION=3.0.0
set SKIP_GENERATE_AUTHORS=1
set SKIP_WRITE_GIT_CHANGELOG=1

python -m pip install --upgrade --no-cache-dir https://github.com/andrew-ma/sim_csv_gui/archive/main.zip
```

Linux
```
export PBR_VERSION=3.0.0
export SKIP_GENERATE_AUTHORS=1
export SKIP_WRITE_GIT_CHANGELOG=1

python3 -m pip install --upgrade --no-cache-dir https://github.com/andrew-ma/sim_csv_gui/archive/main.zip
```

#### Method #2
Windows
```
git clone https://github.com/andrew-ma/sim_csv_gui
cd sim_csv_gui
python -m pip install --upgrade --no-cache-dir .
```

Linux
```
git clone https://github.com/andrew-ma/sim_csv_gui
cd sim_csv_gui
python3 -m pip install --upgrade --no-cache-dir .
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
