@echo off
setlocal enabledelayedexpansion

echo.
echo Starting full project build (with RSA + AES encryption)...
set STARTTIME=%TIME%

:: Step 0: Check if model yolov8n.pt exists; if not, download it
if not exist "yolov8n.pt" (
    echo yolov8n.pt not found, downloading from Ultralytics...
    python scripts\download_yolo.py || goto :error_download
    echo Download completo.
)

:: Step 1: Generate RSA keys
echo Generating RSA key pair...
python scripts/generate_key.py

:: Step 2: Encrypt model with AES and RSA
echo Encrypting model with AES and RSA...
python scripts/encrypt_model.py

:: Step 3: Test BEFORE obfuscation (dev mode)
echo.
echo === Testando codigo antes da ofuscacao (modo desenvolvedor) ===
python main.py
echo.

:: Step 4: Obfuscate source files with PyArmor
echo Obfuscating files with PyArmor...
pyarmor gen main.py scripts/ --output dist_protected --recursive

:: Step 5: gerar hashes para produção após ofuscação
echo Generating SHA-256 hashes for integrity check (prod)...
python scripts/embed_hash.py

:: Step 6: copiar keys, model e hash_registry_obfuscated para dist_protected
xcopy key dist_protected\key\ /E /I /Y >nul
xcopy model dist_protected\model\ /E /I /Y >nul
xcopy dist_protected\hash_registry_obfuscated.py dist_protected\ /Y >nul

:: Step 7: Test AFTER obfuscation (prod mode)
echo.
echo === Testando codigo apos ofuscacao (modo producao) ===
cd dist_protected
python main.py
cd ..
echo.

:: Track build time
set ENDTIME=%TIME%

:: Remove vírgula dos milissegundos e converte para segundos
for /F "tokens=1-3 delims=:," %%a in ("%STARTTIME%") do (
    set /A STARTSEC=%%a*3600 + %%b*60 + %%c
)
for /F "tokens=1-3 delims=:," %%a in ("%ENDTIME%") do (
    set /A ENDSEC=%%a*3600 + %%b*60 + %%c
)

:: Corrige diferença de data (caso o script passe da meia-noite)
if !ENDSEC! LSS !STARTSEC! (
    set /A ENDSEC+=86400
)

set /A DURATION=!ENDSEC! - !STARTSEC!
set /A MINUTES=!DURATION! / 60
set /A SECONDS=!DURATION! %% 60

goto :end

:error_download
echo.
echo [ERRO] Falha ao baixar yolov8n.pt. Verifique sua conexão ou instalação da biblioteca Ultralytics.
exit /b 1

:end
pause
