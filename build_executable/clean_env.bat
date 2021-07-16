:: # Copy and paste these commands first
::conda deactivate
::conda env remove -n temp_build -y
::conda create -n temp_build python=3.7 -y
::conda activate temp_build
::#conda install conda-forge::numpy "blas=*=openblas"
@echo off
echo Deleting "build", "dist", and "venv" ...
del /s /q build dist venv >nul 2>&1
rmdir /s /q build dist venv >nul 2>&1
echo Creating new venv
%MY_PYTHON% -m venv venv
venv\Scripts\activate