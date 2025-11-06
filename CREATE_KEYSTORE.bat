@echo off
REM Create debug.keystore with suzi alias

echo Creating debug.keystore...

keytool -genkeypair ^
    -alias suzi ^
    -keyalg RSA ^
    -keysize 2048 ^
    -validity 10000 ^
    -keystore debug.keystore ^
    -storepass android ^
    -keypass android ^
    -dname "CN=Suzi Studio, OU=Development, O=Suzi, L=Tehran, ST=Tehran, C=IR"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Success! debug.keystore created
    echo ========================================
    echo.
    echo Alias: suzi
    echo Password: android
    echo File: debug.keystore
    echo.
) else (
    echo.
    echo ========================================
    echo Error: Failed to create keystore
    echo ========================================
    echo.
    echo Make sure Java is installed:
    echo   java -version
    echo.
)

pause
