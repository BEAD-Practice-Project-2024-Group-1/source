@echo off

REM =============================
REM load env variables from .env
REM =============================
for /F "tokens=1,2 delims==" %%A in (.env) do (
    REM check if the line starts with #
    echo %%A | findstr /b "#" > nul

    REM if line doesn't start with #
    if errorlevel 1 (
        set %%A=%%B
    )
)

REM =============================
REM replace ./ with absolute path
REM =============================
REM get absolute path of current directory
for %%I in (.) do set CURRENT_DIR=%%~fI

REM iterate over docker-compose.yml to replace paths
setlocal enabledelayedexpansion
for /F "delims=" %%L in (docker-compose.yml) do (
    set "LINE=%%L"
    set UPDATED_LINE=!LINE:./=%CURRENT_DIR%\!
    echo !UPDATED_LINE! >> docker-compose_windows.yml
)
setlocal DisableDelayedExpansion