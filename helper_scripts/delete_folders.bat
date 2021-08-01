@echo off
echo Deleting folders: %*
rmdir /s /q %* >nul 2>&1