# Build Executable Steps (Windows)

1. Change directory to build_executable folder.
```
cd build_executable
```

2. Set required environment variables.
```
set "APP_NAME=sim_csv_gui"
```


3. Ensure python is installed and added to PATH.
> Running "`%MY_PYTHON% -m venv -h`" should not result in an error


4. Download UPX at https://github.com/upx/upx/releases/latest, and extract it.  Set the `UPX_PATH` environment variable to the extracted upx directory.
```
set "UPX_PATH=upx-3.96-win64"
dir %UPX_PATH%
```

5. Run in cmd prompt.
```
make_executable
```

6. Releases are created in _build_executable/dist/_ folder.
   * executable

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