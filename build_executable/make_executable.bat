@echo off
set "MY_PYTHON=python"

if defined UPX_PATH (
    echo UPX_PATH=%UPX_PATH%
) else (
    echo UPX_PATH environment variable is not defined
    exit /b
)

if defined APP_NAME (
    echo APP_NAME=%APP_NAME%
) else (
    echo APP_NAME environment variable is not defined
    exit /b
)

:: Delete folders
call ..\helper_scripts\delete_folders.bat build dist venv

:: Create new venv
call ..\helper_scripts\clean_env.bat

%MY_PYTHON% -m pip install --upgrade pip
%MY_PYTHON% -m pip install wheel setuptools
%MY_PYTHON% -m pip install -r ..\requirements.txt
%MY_PYTHON% -m pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip


:: Run Pyinstaller to generate executable and embeddable zip folder
call run_pyinstaller.bat

:: For embeddable zip folder, move files to lib/ to reduce clutter
:: %MY_PYTHON% move_dist_lib_files.py

:: Zip the Folder
:: cd dist && tar.exe -a -c -f %APP_NAME%.zip %APP_NAME%

:: Delete folders except for dist
call ..\helper_scripts\delete_folders.bat build

echo Done!

:: Deactivate the venv
deactivate
