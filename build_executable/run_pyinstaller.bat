pyinstaller -n %APP_NAME% --icon=sim_icon.ico --upx-dir=%UPX_PATH% --clean "../src/sim_csv_gui/app.py" --runtime-hook add_lib.py --noconsole -y --onedir
:: for DEBUG add '--noupx --debug bootloader'

del /s /q build
rmdir /s /q build