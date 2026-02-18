@echo off
setlocal

echo Installing/Updating build dependencies...
py -m pip install -U nuitka zstandard ordered-set
if errorlevel 1 goto :fail

echo Building SamsungMDCDashboard.exe with Nuitka...
py -m nuitka --onefile --standalone --windows-console-mode=disable --output-filename=SamsungMDCDashboard.exe launch_dashboard.py
if errorlevel 1 goto :fail

echo.
echo Build completed.
echo Check Nuitka output folder for SamsungMDCDashboard.exe
goto :eof

:fail
echo.
echo Build failed.
exit /b 1
