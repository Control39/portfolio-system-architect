@echo off
REM Основной скрипт запуска для Windows
REM Автоматически определяет, какой скрипт использовать

echo ============================================
echo  Система автоматизации расширений VS Code
echo ============================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не найден. Установите Python 3.10+ и добавьте в PATH.
    pause
    exit /b 1
)

REM Проверяем наличие VS Code
code --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] VS Code не найден в PATH.
    echo Проверяем альтернативные пути...

    set FOUND=0
    if exist "%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd" (
        set "CODEPATH=%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"
        set FOUND=1
    )
    if exist "%ProgramFiles%\Microsoft VS Code\bin\code.cmd" (
        set "CODEPATH=%ProgramFiles%\Microsoft VS Code\bin\code.cmd"
        set FOUND=1
    )

    if %FOUND%==0 (
        echo [ОШИБКА] VS Code не найден. Установите VS Code.
        pause
        exit /b 1
    ) else (
        echo VS Code найден по пути: %CODEPATH%
    )
)

REM Определяем действие
set ACTION=check
set CONFIG=config/vscode/vscode-extensions.json
set DRYRUN=

:parse_args
if "%1"=="" goto run_script
if "%1"=="--install" set ACTION=install & shift & goto parse_args
if "%1"=="--sync" set ACTION=sync & shift & goto parse_args
if "%1"=="--check" set ACTION=check & shift & goto parse_args
if "%1"=="--report" set ACTION=report & shift & goto parse_args
if "%1"=="--dry-run" set DRYRUN=--dry-run & shift & goto parse_args
if "%1"=="--config" (
    set CONFIG=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--help" goto show_help
echo [ПРЕДУПРЕЖДЕНИЕ] Неизвестный аргумент: %1
shift
goto parse_args

:show_help
echo.
echo Использование: vscode-extensions-manager.bat [ОПЦИИ]
echo.
echo Опции:
echo   --install        Установить отсутствующие обязательные расширения
echo   --sync           Полная синхронизация
echo   --check          Проверить соответствие ^(по умолчанию^)
echo   --report         Сгенерировать отчет
echo   --dry-run        Режим предварительного просмотра
echo   --config PATH    Путь к конфигурационному файлу
echo   --help           Показать эту справку
echo.
echo Примеры:
echo   vscode-extensions-manager.bat --check
echo   vscode-extensions-manager.bat --sync --dry-run
echo   vscode-extensions-manager.bat --install --config my-config.json
echo.
pause
exit /b 0

:run_script
echo Запуск с параметрами:
echo   Действие: %ACTION%
echo   Конфигурация: %CONFIG%
if not "%DRYRUN%"=="" echo   Режим: Dry Run
echo.

REM Проверяем, какой скрипт использовать
echo Проверяем доступные варианты...
if exist "scripts\vscode-extensions-manager.py" (
    echo Используем Python скрипт...
    python scripts\vscode-extensions-manager.py --action %ACTION% --config "%CONFIG%" %DRYRUN%
) else if exist "scripts\vscode-extensions-windows.ps1" (
    echo Используем PowerShell скрипт...
    powershell -ExecutionPolicy Bypass -File "scripts\vscode-extensions-windows.ps1" -ConfigPath "%CONFIG%" %DRYRUN%
    if "%ACTION%"=="install" powershell -ExecutionPolicy Bypass -File "scripts\vscode-extensions-windows.ps1" -Install -ConfigPath "%CONFIG%" %DRYRUN%
    if "%ACTION%"=="sync" powershell -ExecutionPolicy Bypass -File "scripts\vscode-extensions-windows.ps1" -Sync -ConfigPath "%CONFIG%" %DRYRUN%
    if "%ACTION%"=="check" powershell -ExecutionPolicy Bypass -File "scripts\vscode-extensions-windows.ps1" -Check -ConfigPath "%CONFIG%" %DRYRUN%
    if "%ACTION%"=="report" powershell -ExecutionPolicy Bypass -File "scripts\vscode-extensions-windows.ps1" -Report -ConfigPath "%CONFIG%" %DRYRUN%
) else (
    echo [ОШИБКА] Не найден ни один скрипт управления расширениями.
    echo Убедитесь, что файлы находятся в папке scripts\.
    pause
    exit /b 1
)

echo.
echo ============================================
if %errorlevel% equ 0 (
    echo Скрипт завершен успешно.
) else (
    echo Скрипт завершен с ошибкой.
)
echo ============================================
pause
