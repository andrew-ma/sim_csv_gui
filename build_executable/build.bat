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

call clean_env.bat
call install_requirements.bat
call run_pyinstaller.bat
%MY_PYTHON% move_dist_lib_files.py

cd dist && tar.exe -a -c -f %APP_NAME%.zip %APP_NAME%