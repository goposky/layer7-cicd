@echo off

:: This is the directory that the Jar is in. Assumed to be the same directory as the.bat file
set jarDir=%~dp0

SETLOCAL 

::clear the variable, 
set JAVA_TO_USE=

if "%1" == "--jdk" (
    :: gets the jdk path form the --jdk option
    SHIFT
    call:getJavaPath %%1
    SHIFT
) else IF DEFINED JAVA_HOME (
    :: gets the java path from the JAVA_HOME property
    call:getJavaPath "%JAVA_HOME%"
) else (   
    :: checks if the java executable is in the PATH, search the environment path    
    for %%G in ("%path:;=" "%") do (
       for %%I in (java.bat java.exe) do (    
            if exist %%G\%%I (   
                set JAVA_TO_USE=%%G\%%I
                goto :break
            )
        )
    )
)
:break


if not exist "%JAVA_TO_USE%" (
    echo Please ensure "java" is in the PATH, set JAVA_HOME or run with --jdk option.
    exit /B 1
)

set ARGS=
set JDK_version=1.8

for /f tokens^=2-3^ delims^=.-_^" %%j in ('"%JAVA_TO_USE%" -fullversion 2^>^&1') do set "version=%%j.%%k"
if %version% LSS %JDK_version% (
    echo Java %JDK_version% is required, but %version% was found.
    exit /b 1
) else (
    ::get all the remaining args, can't use %* here because it contains all original args, shift does not affect %*
    :parse
    if not "%~1" == "" (
        set ARGS=%ARGS% %1
        SHIFT
        goto :parse
    )
    "%JAVA_TO_USE%" -Dfile.encoding=UTF-8  -DGMU_HOME="%jarDir%." -jar "%jarDir%GatewayMigrationUtility.jar" %ARGS%
)

goto:eof

::--------------------------------------------------------
::-- Function section starts below here
::--------------------------------------------------------

::gets the java path from the given folder, checking if the java.exe file exists
:getJavaPath
    if exist %~1\bin\java.exe (
        set JAVA_TO_USE=%~1\bin\java.exe        
    )     
    
GOTO:EOF
ENDLOCAL 
