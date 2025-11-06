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
set TEMP_LOST_PINGS=%TEMP%\icmp_dashboard_lost_%RANDOM%.txt

REM Initialize temp file for tracking lost pings
if exist "%TEMP_LOST_PINGS%" del "%TEMP_LOST_PINGS%"
echo. > "%TEMP_LOST_PINGS%"

:INIT
cls
echo ================================================================================
echo                   ICMP DASHBOARD - Monitoring: %TARGET%
echo ================================================================================
echo.
echo Initializing dashboard...
echo Note: Press Ctrl+C to stop and see final statistics
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

REM Log lost ping with timestamp
echo %DATE% %TIME% >> "%TEMP_LOST_PINGS%"

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
echo Press Ctrl+C to exit and see final statistics
echo.
timeout /t 1 /nobreak >nul
goto MAIN

REM This section will be reached if user closes gracefully
:CLEANUP
cls
echo.
echo ================================================================================
echo                         FINAL STATISTICS
echo ================================================================================
echo.
echo Total Pings    : %TOTAL%
echo Successful     : %SUCCESS%
echo Failed         : %FAILED%

if %TOTAL% GTR 0 (
    set /a LOSS=%FAILED%*100/%TOTAL%
    echo Packet Loss    : !LOSS!%%
)

if %SUCCESS% GTR 0 (
    set /a AVG=%SUM%/%SUCCESS%
    echo.
    echo Avg Time       : !AVG!ms
    echo Min Time       : %MIN%ms
    echo Max Time       : %MAX%ms
)

REM Display lost ping summary if there were failures
if %FAILED% GTR 0 (
    echo.
    echo ================================================================================
    echo                         LOST PING DETAILS
    echo ================================================================================
    echo.

    REM Read and display lost ping timestamps
    set PING_COUNT=0
    for /f "usebackq delims=" %%a in ("%TEMP_LOST_PINGS%") do (
        set LINE=%%a
        if not "!LINE!"=="" (
            set /a PING_COUNT+=1
            echo   Lost ping #!PING_COUNT!: %%a
        )
    )

    if !PING_COUNT! EQU 0 (
        echo   No lost ping records found
    )
)

echo.
echo ================================================================================
echo.
echo Dashboard stopped.

REM Cleanup temp file
if exist "%TEMP_LOST_PINGS%" del "%TEMP_LOST_PINGS%"

pause
exit /b
