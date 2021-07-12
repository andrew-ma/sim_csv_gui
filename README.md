# SIM CSV GUI
Powered by sim_csv_script
GUI to read and write SIM cards.
Fields and values are specified in a CSV file, and optionally a filter script can be supplied for dynamically changing the CSV contents for each card.

## Download Windows Executable
https://github.com/andrew-ma/sim_csv_gui/releases/latest

---
## Download Python Package (for other OS and platforms)
### System Requirements
* Python 3.7 or later ([Python Installation Steps](python_installation_steps.md))

### Python Package Dependencies:
* sim_csv_script @ https://github.com/andrew-ma/sim_csv_script/archive/main.zip
* PyQt5

### Installation
```
pip install https://github.com/andrew-ma/sim_csv_gui/archive/main.zip --upgrade --no-cache-dir
```
> _Linux_: if you get a "swig: not found" error while running the installation command, first ensure that Python 3.7 or later is installed ('`python3 --version`').  If so, install swig with '`sudo apt install swig`' and retry the installation command.


### Uninstall
```
pip uninstall sim_csv_gui -y
```

---
### __Graphical User Interface__

Launch GUI
```
sim_csv_gui
```

---

## For [Development Documentation](development.md)
