@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo  Run setup.bat first. & pause & exit /b 1)
call ".venv\Scripts\activate.bat"
echo  Writing this week's 3 LinkedIn posts ...
python scout.py posts
for /f "delims=" %%d in ('python -c "import datetime; print(datetime.date.today().isoformat())"') do set "TODAY=%%d"
if exist "..\data\outbox\%TODAY%\today.html" start "" "..\data\outbox\%TODAY%\today.html"
pause
