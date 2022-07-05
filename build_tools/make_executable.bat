@echo off
:: UPX is required
if defined UPX_PATH (
    echo UPX_PATH=%UPX_PATH%
    if not exist "%UPX_PATH%\" (
        echo UPX_PATH folder does not exist
        exit /b 1
    )
) else (
    echo UPX_PATH environment variable is not defined
    exit /b 1
)

:: Setting Environment Variables
set MY_PYTHON=python
set PACKAGE_NAME=sim_csv_gui
set SKIP_GENERATE_AUTHORS=1
set SKIP_WRITE_GIT_CHANGELOG=1

:: Delete folders
call :delete_folders build dist venv .eggs src\%PACKAGE_NAME%.egg-info .qt_for_python __pycache__

:: Delete files
call :delete_files *.spec

:: Create new virtual environment
call :new_venv
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: Upgrade Pip version
%MY_PYTHON% -m pip install --upgrade pip

:: Installing Build Dependencies
%MY_PYTHON% -m pip install wheel setuptools

:: Installing Dependencies from requirements.txt
%MY_PYTHON% -m pip install -r ..\requirements.txt

:: Install latest version of Pyinstaller
%MY_PYTHON% -m pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip

:: Generate Standalone Executable ("PACKAGE_NAME.exe")
@echo on
call pyinstaller -n "%PACKAGE_NAME%" --icon=sim_icon.ico --upx-dir="%UPX_PATH%" --clean --noconsole -y --onefile "../src/sim_csv_gui/app.py"
@echo off

echo Finished with error code: %ERRORLEVEL%

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Deactivate the virtual environment
call venv\Scripts\deactivate

:: Delete folders except for dist
call :delete_folders build .eggs src\%PACKAGE_NAME%.egg-info venv .qt_for_python __pycache__

:: Delete files
call :delete_files *.spec

EXIT /B %ERRORLEVEL%

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:delete_folders
echo Deleting folders: %*
rmdir /s /q %* >nul 2>&1
EXIT /B 0


:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:delete_files
echo Deleting files: %*
del /s /q %* >nul 2>&1
EXIT /B 0


:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:new_venv
echo Creating new temporary python virtual environment
%MY_PYTHON% -m venv venv
call venv\Scripts\activate
EXIT /B 0
