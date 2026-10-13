@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo  Drag your verified Apollo CSV file onto leads.bat.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (echo  Run setup.bat first. & pause & exit /b 1)
call ".venv\Scripts\activate.bat"
python autopilot.py leads --in "%~1"
if errorlevel 3 if not errorlevel 4 (
  echo.
  choice /m " This batch costs more than the safety limit shown above. Run it anyway"
  if errorlevel 2 (echo  Stopped. Nothing was spent. & pause & exit /b 0)
  python autopilot.py leads --in "%~1" --yes
)
echo.
echo  Open the -ready.csv file next to your Apollo file. Check 20 rows: first_line against probe_answer.
pause
