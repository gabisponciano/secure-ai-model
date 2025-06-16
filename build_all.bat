@echo off
setlocal enabledelayedexpansion

echo.
echo [🚀] Iniciando build completa do projeto...
set STARTTIME=%TIME%

:: Etapa 1: Geração de chave, modelo e criptografia
echo [🔑] Gerando chave secreta...
python scripts/generate_key.py

echo [📦] Gerando e salvando modelo...
python scripts/save_model.py

echo [🔐] Criptografando modelo...
python scripts/encrypt_model.py

:: Etapa 2: Ofuscação com PyArmor
echo [🛡️] Ofuscando arquivos com PyArmor...
pyarmor gen src/main.py scripts/ --output dist_protected --recursive

:: Etapa 3: Cópia das pastas key e model para o dist_protected
echo [📁] Copiando pastas key e model...
xcopy key dist_protected\key\ /E /I /Y >nul
xcopy model dist_protected\model\ /E /I /Y >nul

:: Etapa 4: Compilação com PyInstaller (gerando o .exe em dist/)
echo [📦] Empacotando executável com PyInstaller...
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


:: Cronometrar o tempo de execução
:: Cronometrar o tempo de execução
echo.
set ENDTIME=%TIME%

:: Converter horários para segundos
for /F "tokens=1-3 delims=:.," %%a in ("%STARTTIME%") do (
    set /A STARTSEC=%%a*3600 + %%b*60 + %%c
)
for /F "tokens=1-3 delims=:.," %%a in ("%ENDTIME%") do (
    set /A ENDSEC=%%a*3600 + %%b*60 + %%c
)

:: Lidar com virada de dia (END < START)
if !ENDSEC! LSS !STARTSEC! (
    set /A ENDSEC+=86400
)

set /A DURATION=!ENDSEC! - !STARTSEC!
set /A MINUTES=!DURATION! / 60
set /A SECONDS=!DURATION! %% 60

echo [✅] Processo concluído!
echo 🔄 Tempo total: %STARTTIME% → %ENDTIME%
echo ⏱️  Duração total: !MINUTES! minuto(s) e !SECONDS! segundo(s)

pause

