@echo off

:: Requiered dependency: pyinstaller
:: See: https://pyinstaller.org/en/stable/

echo Removing old deployment (if exists)...
if exist dist rmdir /s /q dist

echo Installing sound_driver...
pyinstaller sound_driver.py > NUL 2>&1
copy config.yaml dist\sound_driver\ > NUL 2>&1

echo Creating a zip file...
powershell Compress-Archive -Path dist\sound_driver -DestinationPath sound_driver.zip -Update

echo Installation done
