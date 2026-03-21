@echo off
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py app.py
  goto :eof
)

where python >nul 2>nul
if %errorlevel%==0 (
  python app.py
  goto :eof
)

echo Python hittades inte. Installera Python 3 och prova igen.
pause
