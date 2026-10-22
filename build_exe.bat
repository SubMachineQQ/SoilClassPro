@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"
set "PY="

echo Looking for Python...

for %%V in (.venv venv env) do (
    if exist "%%V\Scripts\python.exe" (
        set "PY=%%~fV\Scripts\python.exe"
        goto :found
    )
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PY=py -3"
    goto :found
)

python --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%A in ('python --version 2^>^&1') do set "VER=%%A"
    if not "!VER!"=="" (
        set "PY=python"
        goto :found
    )
)

for /f "delims=" %%P in ('dir /b /ad /o-n "%LOCALAPPDATA%\Programs\Python\Python3*" 2^>nul') do (
    if exist "%LOCALAPPDATA%\Programs\Python\%%P\python.exe" (
        set "PY=%LOCALAPPDATA%\Programs\Python\%%P\python.exe"
        goto :found
    )
)
for /f "delims=" %%P in ('dir /b /ad /o-n "C:\Python3*" 2^>nul') do (
    if exist "C:\%%P\python.exe" (
        set "PY=C:\%%P\python.exe"
        goto :found
    )
)
for /f "delims=" %%P in ('dir /b /ad /o-n "%ProgramFiles%\Python3*" 2^>nul') do (
    if exist "%ProgramFiles%\%%P\python.exe" (
        set "PY=%ProgramFiles%\%%P\python.exe"
        goto :found
    )
)

echo.
echo ============================================================
echo  Python was not found.
echo.
echo  Checked: .venv / venv / env in this folder, the "py"
echo  launcher, "python" on PATH, and the usual install folders.
echo.
echo  Install it from https://www.python.org/downloads/ and tick
echo  "Add python.exe to PATH" on the first screen of the
echo  installer, then re-run this script.
echo.
echo  If Python IS installed (e.g. through Visual Studio), open a
echo  command prompt in this folder and run the build by hand:
echo      "C:\path\to\python.exe" -m pip install pyinstaller
echo      "C:\path\to\python.exe" -m PyInstaller --onefile ...
echo ============================================================
pause
exit /b 1

:found
echo Using: %PY%
%PY% --version
echo.

echo Installing/updating PyInstaller...
%PY% -m pip install --upgrade pip pyinstaller || goto :error

echo.
echo Installing project requirements...
%PY% -m pip install --upgrade -r requirements.txt || goto :error

echo.
echo Building SoilClassPro.exe ...
%PY% -m PyInstaller --noconfirm --clean SoilClassPro.spec || goto :error

echo.
echo ============================================================
echo  Done! Your executable is at:  dist\SoilClassPro.exe
echo ============================================================
pause
exit /b 0

:error
echo.
echo Build failed - see the messages above.
pause
exit /b 1
