@echo off
setlocal

set SITE_PKG=C:\Users\Ionut.Emilian\AppData\Local\Programs\Python\Python313\Lib\site-packages

echo ============================================
echo  SamsungPy - Building standalone EXE
echo ============================================

py -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "SamsungMDCDashboard" ^
    --add-data "%SITE_PKG%\customtkinter;customtkinter" ^
    --add-data "%SITE_PKG%\darkdetect;darkdetect" ^
    --hidden-import customtkinter ^
    --hidden-import darkdetect ^
    --hidden-import samsung_mdc ^
    --hidden-import PIL ^
    --hidden-import PIL._tkinter_finder ^
    launch_dashboard.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  BUILD SUCCESSFUL!
echo  EXE is at:  dist\SamsungMDCDashboard.exe
echo  Copy that single file to any Windows PC.
echo ============================================
pause
