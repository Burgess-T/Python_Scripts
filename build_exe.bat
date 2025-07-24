@echo off
setlocal enabledelayedexpansion

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing now...
    pip install --upgrade pyinstaller
)

REM Prompt user for Python script filename
:get_filename
echo Enter the Python script filename (e.g., myscript.py):
set /p "python_file=>> "

REM Validate input
if not defined python_file (
    echo Error: No filename entered. Please try again.
    goto :get_filename
)

if not exist "%python_file%" (
    echo Error: File "%python_file%" does not exist.
    goto :get_filename
)

REM Ask user about console preference
echo.
echo Select console option:
echo 1. No console (recommended for GUI apps)
echo 2. With console (required for CLI apps using input())
set /p "console_opt=Enter choice [1-2]: "

REM Set console option based on user choice
if "!console_opt!"=="1" (
    set "console_option=--noconsole"
) else if "!console_opt!"=="2" (
    set "console_option=--console"
) else (
    echo Invalid choice. Defaulting to no console.
    set "console_option=--noconsole"
)

REM Extract filename without extension for EXE name
for %%i in ("%python_file%") do (
    set "exe_name=%%~ni"
    set "script_dir=%%~dpi"
)

REM Set packaging options
set "options=--onefile --clean !console_option! --name "%exe_name%" --distpath "dist_temp" --workpath "build_temp" --specpath "spec_temp""

REM Execute packaging command
echo.
echo Packaging "%python_file%"...
pyinstaller %options% "%python_file%"

REM Check if EXE was created
set "exe_path=dist_temp\%exe_name%.exe"
if exist "%exe_path%" (
    echo Moving .exe file...
    REM Move EXE to original script directory
    move /Y "%exe_path%" "%script_dir%" >nul
    echo EXE file saved to: "%script_dir%%exe_name%.exe"
    
    REM Clean up temporary files
    echo Cleaning temporary files...
    rmdir /S /Q "dist_temp" 2>nul
    rmdir /S /Q "build_temp" 2>nul
    rmdir /S /Q "spec_temp" 2>nul
    del "%~dp0%exe_name%.spec" 2>nul

    echo Packaging successful!
) else (
    echo.
    echo Packaging failed. Please check error messages.
    echo Temporary files kept for debugging.
)

endlocal
pause