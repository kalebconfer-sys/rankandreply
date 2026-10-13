@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo  Drag your exported replies CSV file onto replies.bat.
  echo  Columns needed: email, first_name, company, website, reply_text
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (echo  Run setup.bat first. & pause & exit /b 1)
call ".venv\Scripts\activate.bat"
python autopilot.py replies --in "%~1"
for /f "delims=" %%d in ('python -c "import datetime; print(datetime.date.today().isoformat())"') do set "TODAY=%%d"
if exist "..\data\outbox\%TODAY%\today.html" start "" "..\data\outbox\%TODAY%\today.html"
pause
