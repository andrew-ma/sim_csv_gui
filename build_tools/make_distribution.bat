@echo off
:: Setting Environment Variables
set MY_PYTHON=python
set PACKAGE_NAME=sim_csv_gui
set SKIP_GENERATE_AUTHORS=1
set SKIP_WRITE_GIT_CHANGELOG=1

:: Change directory to directory containing the setup.py, which is the parent directory
pushd ..

:: Delete folders
call :delete_folders build dist venv .eggs ..\src\%PACKAGE_NAME%.egg-info .qt_for_python __pycache__

:: Create new virtual environment
@REM call :new_venv
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: Upgrade Pip version
@REM %MY_PYTHON% -m pip install --upgrade pip

:: Installing Build Dependencies
@REM %MY_PYTHON% -m pip install wheel setuptools

:: Installing Dependencies from requirements.txt
@REM %MY_PYTHON% -m pip install -r requirements.txt

:: Generate Source Distribution ("PACKAGE_NAME-VERSION.tar.gz") in dist/ folder
@echo on
%MY_PYTHON% setup.py sdist
@echo off

echo Finished with error code: %ERRORLEVEL%

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Deactivate the virtual environment
@REM call venv\Scripts\deactivate

:: Delete folders except for dist
call :delete_folders build .eggs ..\src\%PACKAGE_NAME%.egg-info venv .qt_for_python __pycache__

:: Change directory to original folder (where this script is run from)
popd

EXIT /B %ERRORLEVEL%

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:delete_folders
echo Deleting folders: %*
rmdir /s /q %* >nul 2>&1
EXIT /B 0

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:new_venv
echo Creating new temporary python virtual environment
%MY_PYTHON% -m venv venv
call venv\Scripts\activate
EXIT /B 0
