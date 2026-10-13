@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo  Run setup.bat first. & pause & exit /b 1)
call ".venv\Scripts\activate.bat"
echo  Finding new Reddit, Hacker News and Upwork posts and drafting replies ...
python scout.py run
call :open_today
pause
exit /b 0

:open_today
for /f "delims=" %%d in ('python -c "import datetime; print(datetime.date.today().isoformat())"') do set "TODAY=%%d"
if exist "..\data\outbox\%TODAY%\today.html" start "" "..\data\outbox\%TODAY%\today.html"
exit /b 0
