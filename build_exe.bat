@echo off
cd /d "%~dp0"

echo ========================================
echo   ECOdata - Build do executavel
echo ========================================
echo.

echo [1/4] Baixando DLLs do Firebird...
if not exist "firebird_dll\*.dll" (
    echo Baixando Firebird 4.0.7 x64...
    powershell -Command "& { $d='firebird_dll'; $u='https://github.com/FirebirdSQL/firebird/releases/download/v4.0.7/Firebird-4.0.7.3271-0-x64.zip'; $z=\"$env:TEMP\fb_x64.zip\"; Write-Host 'Baixando 23 MB...'; $wc=New-Object System.Net.WebClient; $wc.DownloadFile($u,$z); Add-Type -AssemblyName System.IO.Compression.FileSystem; $f=[System.IO.Compression.ZipFile]::OpenRead($z); $f.Entries | Where-Object { $_.Name -in @('fbclient.dll','ib_util.dll') } | ForEach-Object { [System.IO.Compression.ZipFileExtensions]::ExtractToFile($_,\"$d\\$($_.Name)\",$true) }; $f.Dispose(); Remove-Item $z -Force; Write-Host 'OK' }"
) else (
    echo DLLs ja existentes.
)

echo.
echo [2/4] Instalando dependencias Python...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias
    exit /b %errorlevel%
)

echo.
echo [3/4] Build do frontend Vue.js...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERRO] Falha no npm install
    exit /b %errorlevel%
)
call npm run build
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao buildar frontend
    exit /b %errorlevel%
)
cd ..

echo.
echo [4/4] Gerando executavel com PyInstaller...
pyinstaller --clean ecodata.spec
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao gerar executavel
    exit /b %errorlevel%
)

echo.
echo ========================================
echo   OK! Executavel gerado em:
echo   dist\ecodata.exe
echo ========================================
pause
