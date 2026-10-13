@echo off
setlocal
cd /d "%~dp0"
echo.
echo  ===== Rank and Reply: one-time setup =====
echo.

set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if defined PY (
  %PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
  if errorlevel 1 set "PY="
)
if not defined PY (
  echo  Python 3.10 or newer is not installed yet.
  echo  Opening the download page. Install it, and on the first screen TICK
  echo  "Add python.exe to PATH". Then double-click setup.bat again.
  start "" https://www.python.org/downloads/
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo  Creating a private Python environment in .venv ...
  %PY% -m venv .venv || (echo  Could not create .venv & pause & exit /b 1)
)
call ".venv\Scripts\activate.bat"

echo  Installing the tools (a few minutes the first time) ...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt || (echo  Install failed. Copy the error into Claude Code. & pause & exit /b 1)
echo  Installing the browser used for PDF reports ...
python -m playwright install chromium

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo  Created .env for your keys.
)

echo.
echo  ===== Which AIs are connected =====
python council.py status
echo.
echo  Next: paste your API keys into .env (it opens now), save it, and run setup.bat
echo  again to check every line says "ready". Day-by-day steps: business\02-plan\day-by-day.md
notepad ".env"
pause
