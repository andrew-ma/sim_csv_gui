@echo off
%MY_PYTHON% -m pip install wheel setuptools
%MY_PYTHON% -m pip install -r ..\requirements.txt
%MY_PYTHON% -m pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip
