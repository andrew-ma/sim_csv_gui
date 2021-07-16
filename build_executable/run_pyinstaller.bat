@echo off
:: GENERATE DIRECTORY FOR ZIP FILE
:: pyinstaller -n "%APP_NAME%" --icon=sim_icon.ico --upx-dir="%UPX_PATH%" --clean "../src/sim_csv_gui/app.py" --runtime-hook add_lib.py --noconsole -y --onedir
:: for DEBUG add '--noupx --debug bootloader'

:: GENERATE SINGLE EXE FILE
pyinstaller -n "%APP_NAME%" --icon=sim_icon.ico --upx-dir="%UPX_PATH%" --clean "../src/sim_csv_gui/app.py" --noconsole -y --onefile

:: CLEANUP
del /s /q build >nul 2>&1
rmdir /s /q build >nul 2>&1
