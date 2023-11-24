@echo off

:: Requiered dependency: pyinstaller
:: See: https://pyinstaller.org/en/stable/

echo Removing old deployment if exists...
rmdir /s /q dist

echo Installing sound_driver...
pyinstaller sound_driver.py
copy config.yaml dist\sound_driver\

powershell Compress-Archive -Path dist\sound_driver -DestinationPath sound_driver.zip

echo Installation done
