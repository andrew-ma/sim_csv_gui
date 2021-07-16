@echo off
if defined MY_PYTHON (
    echo MY_PYTHON=%MY_PYTHON%
) else (
    echo MY_PYTHON environment variable is not defined
    exit /b
)

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

:: Create new venv
call clean_env.bat

%MY_PYTHON% -m pip install --upgrade pip

:: Install pip requirements
call install_requirements.bat

:: Run Pyinstaller to generate executable and embeddable zip folder
call run_pyinstaller.bat

:: For embeddable zip folder, move files to lib/ to reduce clutter
:: %MY_PYTHON% move_dist_lib_files.py

:: Zip the Folder
:: cd dist && tar.exe -a -c -f %APP_NAME%.zip %APP_NAME%

echo Done!

:: Deactivate the venv
deactivate