@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo ViviendaSeg: abre http://127.0.0.1:8000 en el navegador.
echo.
where py >nul 2>&1
if %errorlevel%==0 (
  py app.py
) else (
  python app.py
)
echo.
echo Pulsa una tecla para cerrar esta ventana.
pause >nul
