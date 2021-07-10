# Build Executable Steps

* Download UPX at https://github.com/upx/upx/releases/latest, unzip it, and set the environment variable `UPX_PATH` to the directory
```
set "UPX_PATH=C:\Users\srcus\Desktop\just_script\upx-3.96-win64"
set "APP_NAME=SIM CITY"
```

* Run in cmd prompt
```
cd build_executable
deactivate
clean_env.bat
install_requirements.bat
run_pyinstaller.bat
python move_dist_lib_files.py
```

* The final result is in the dist/ folder, and this can be zipped up. Click on the .exe file to run.

---

## Organizing files in dist/ folder
* There are many files in dist/ created by pyinstaller, which is overwhelming. I try to move files to the lib/ subfolder.

* After adding cwd()/lib to path, these are required in top level

        ALL_FOLDERS/
        libopenblas.GK7GX5KEQ4F6UYO3P26ULGBQYHGQO7J4.gfortran-win_amd64.dll
        base_library.zip
        python3.dll
        python39.dll
        Qt5Core.dll
        Qt5Gui.dll
        Qt5Widgets.dll


* After setting sys._MEIPASS to sys._MEIPASS/lib, only these are required in top level

        numpy/
        pandas/
        smartcard/
        base_library.zip
        libopenblas.GK7GX5KEQ4F6UYO3P26ULGBQYHGQO7J4.gfortran-win_amd64.dll
        python39.dll