@echo off
title ECOdata
cd /d "C:\Users\Suporte\Documents\Projetos ECO\ECOdata"

set PORT=8580

:check_port
netstat -ano | findstr ":%PORT%" >nul 2>&1
if %errorlevel% neq 0 goto run
set /a PORT+=1
if %PORT% gtr 8590 goto full
goto check_port

:run
set ECODATA_PORT=%PORT%
echo ========================================
echo  ECOdata iniciando em:
echo  http://localhost:%PORT%
echo ========================================
start http://localhost:%PORT%
call .venv\Scripts\activate.bat
python -m server.app
pause
goto :eof

:full
echo Todas as portas de 8580 a 8590 ocupadas!
pause
