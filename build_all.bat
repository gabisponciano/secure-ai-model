@echo off
setlocal enabledelayedexpansion

echo.
echo Starting full project build...
set STARTTIME=%TIME%

echo Generating secret key...
python scripts/generate_key.py

echo Saving model to file...
python scripts/save_model.py

echo Encrypting model file...
python scripts/encrypt_model.py

:: Step 2: Obfuscation with PyArmor
echo Obfuscating files with PyArmor...
pyarmor gen src/main.py scripts/ --output dist_protected --recursive

:: Step 3: Copy key and model folders to dist_protected
echo Copying key and model folders...
xcopy key dist_protected\key\ /E /I /Y >nul
xcopy model dist_protected\model\ /E /I /Y >nul

:: Step 4: Packaging with PyInstaller (producing .exe in dist/)
echo Packaging executable with PyInstaller...
pyinstaller --onefile dist_protected/main.py ^
  --add-data "dist_protected/key;key" ^
  --add-data "dist_protected/model;model" ^
  --add-data "dist_protected/scripts;scripts" ^
  --collect-all torch ^
  --collect-all ultralytics ^
  --collect-all numpy ^
  --collect-all PIL ^
  --collect-all torchvision ^
  --hidden-import cryptography.fernet ^
  --hidden-import pkg_resources.py2_warn ^
  --hidden-import urllib3 ^
  --hidden-import idna ^
  --hidden-import certifi ^
  --hidden-import charset_normalizer ^
  --name secure_model ^
  --distpath dist ^
  --workpath build ^
  --specpath .

:: Track build time
echo.
set ENDTIME=%TIME%

:: Convert start and end time to seconds
for /F "tokens=1-3 delims=:.," %%a in ("%STARTTIME%") do (
    set /A STARTSEC=%%a*3600 + %%b*60 + %%c
)
for /F "tokens=1-3 delims=:.," %%a in ("%ENDTIME%") do (
    set /A ENDSEC=%%a*3600 + %%b*60 + %%c
)

:: Handle day rollover
if !ENDSEC! LSS !STARTSEC! (
    set /A ENDSEC+=86400
)

set /A DURATION=!ENDSEC! - !STARTSEC!
set /A MINUTES=!DURATION! / 60
set /A SECONDS=!DURATION! %% 60

echo Build process completed!
echo Total time: %STARTTIME% - %ENDTIME%
echo Duration: !MINUTES! minute(s) and !SECONDS! second(s)

pause
