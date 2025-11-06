@echo off
REM ICMP Dashboard - CMD/Batch Version
REM Simple real-time ping monitoring with statistics

setlocal EnableDelayedExpansion

set TARGET=www.google.com
set TOTAL=0
set SUCCESS=0
set FAILED=0
set SUM=0
set MIN=99999
set MAX=0

:INIT
cls
echo ================================================================================
echo                   ICMP DASHBOARD - Monitoring: %TARGET%
echo ================================================================================
echo.
echo Initializing dashboard...
timeout /t 2 /nobreak >nul
goto MAIN

:MAIN
cls
echo ================================================================================
echo                   ICMP DASHBOARD - Monitoring: %TARGET%
echo ================================================================================
echo.
echo [STATISTICS]                          [PING RESULTS]
echo ----------------------------------------
set /a TOTAL+=1

REM Perform ping and capture result
for /f "tokens=5,7 delims=: " %%a in ('ping -n 1 -w 5000 %TARGET% ^| findstr /i "time="') do (
    set "TIME_STR=%%b"
    set "TIME_STR=!TIME_STR:ms=!"
    set /a SUCCESS+=1
    set /a SUM+=!TIME_STR!

    if !TIME_STR! LSS !MIN! set MIN=!TIME_STR!
    if !TIME_STR! GTR !MAX! set MAX=!TIME_STR!

    goto SUCCESS_PING
)

REM Failed ping
set /a FAILED+=1
echo Total Pings    : !TOTAL!              [%TIME%] Request timed out
echo Successful    : !SUCCESS!
echo Failed        : !FAILED!
echo.
if !TOTAL! GTR 0 (
    set /a LOSS=!FAILED!*100/!TOTAL!
    echo Packet Loss   : !LOSS!%%
)
goto CONTINUE

:SUCCESS_PING
echo Total Pings    : !TOTAL!              [%TIME%] Reply from %TARGET%: time=!TIME_STR!ms
echo Successful    : !SUCCESS!
echo Failed        : !FAILED!
echo.
if !TOTAL! GTR 0 (
    set /a LOSS=!FAILED!*100/!TOTAL!
    echo Packet Loss   : !LOSS!%%
)
echo.
if !SUCCESS! GTR 0 (
    set /a AVG=!SUM!/!SUCCESS!
    echo Avg Time      : !AVG!ms
    echo Min Time      : !MIN!ms
    echo Max Time      : !MAX!ms
)

:CONTINUE
echo.
echo ----------------------------------------
echo Press Ctrl+C to exit
echo.
timeout /t 1 /nobreak >nul
goto MAIN
