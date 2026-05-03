@echo off
:: Переменные окружения для Windows 11 для работы с UTF-8 кодировкой
:: Запускайте этот скрипт с правами администратора для глобальной настройки
:: Или добавьте в автозагрузку пользователя для локальной настройки

:: Заголовок
echo.
echo Установка переменных окружения для UTF-8 поддержки
echo ==============================================================================

:: Проверка прав администратора
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Проверка прав: Администраторские права подтверждены
) else (
    echo ПРЕДУПРЕЖДЕНИЕ: Запущено без администраторских прав
    echo Некоторые настройки будут применены только для текущего пользователя
    echo Для полной настройки запустите от имени администратора
    echo.
)

:: Установка системной кодировки UTF-8
:: Эта настройка влияет на cmd.exe и PowerShell
echo.
set REG_PATH="HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Nls\\CodePage"
set VALUE_NAME="ACP"
set VALUE_DATA="65001"

:: Проверяем текущее значение
for /f "tokens=3" %%a in ('reg query %REG_PATH% /v %VALUE_NAME% 2^>nul ^| findstr /i %VALUE_NAME%') do (
    set CURRENT_VALUE=%%a
)

if "%CURRENT_VALUE%"=="%VALUE_DATA%" (
    echo Системная кодировка уже установлена в UTF-8 (65001)
) else (
    echo Установка системной кодировки в UTF-8...
    reg add %REG_PATH% /v %VALUE_NAME% /t REG_SZ /d %VALUE_DATA% /f >nul 2>&1
    if %errorlevel% == 0 (
        echo Успешно: Системная кодировка установлена в UTF-8
    ) else (
        echo ОШИБКА: Не удалось установить системную кодировку
        echo Попробуйте запустить скрипт от имени администратора
    )
)

:: Установка кодировки для нового процесса cmd.exe
setx PYTHONIOENCODING "utf-8" >nul
setx PYTHONLEGACYWINDOWSSTDIO "1" >nul

:: Установка переменных окружения для Git
setx GIT_CONFIG_NOCOMMIT "true" >nul

:: Установка кодировки для PowerShell
:: Создаем или обновляем профиль PowerShell
set POWERSHELL_PROFILE="%USERPROFILE%\\Documents\\WindowsPowerShell\\Microsoft.PowerShell_profile.ps1"

if not exist %POWERSHELL_PROFILE% (
    echo Создание профиля PowerShell...
    mkdir "%USERPROFILE%\\Documents\\WindowsPowerShell" >nul 2>&1
    echo # Профиль PowerShell для поддержки UTF-8 > %POWERSHELL_PROFILE%
)

:: Добавляем настройки UTF-8 в профиль PowerShell
echo.
findstr /c:"[Console]::OutputEncoding = [Text.Encoding]::UTF8" %POWERSHELL_PROFILE% >nul
if %errorlevel% == 0 (
    echo Профиль PowerShell: Настройки UTF-8 уже присутствуют
) else (
    echo [Console]::OutputEncoding = [Text.Encoding]::UTF8 >> %POWERSHELL_PROFILE%
    echo [Console]::InputEncoding = [Text.Encoding]::UTF8 >> %POWERSHELL_PROFILE%
    echo $OutputEncoding = [Console]::OutputEncoding >> %POWERSHELL_PROFILE%
    echo.
    echo Успешно: Настройки UTF-8 добавлены в профиль PowerShell
)

:: Установка кодировки для Windows Terminal (если установлен)
set WT_SETTINGS="%LOCALAPPDATA%\\Packages\\Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\settings.json"

if exist %WT_SETTINGS% (
    echo.
    echo Windows Terminal найден. Проверка настроек...
    findstr /c:""useAcrylic"" %WT_SETTINGS% >nul
    if %errorlevel% == 0 (
        echo Windows Terminal: Настройки уже обновлены
    ) else (
        echo Windows Terminal: Обновление настроек...
        :: Резервное копирование оригинальных настроек
        copy %WT_SETTINGS% "%LOCALAPPDATA%\\Packages\\Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\settings.json.bak" >nul

        :: Добавляем настройки UTF-8 (упрощенный пример)
        echo {
        echo     "profiles": {
        echo         "defaults": {
        echo             "font": {
        echo                 "face": "Consolas",
        echo                 "size": 10
        echo             },
        echo             "locale": "ru_RU.UTF-8"
        echo         }
        echo     },
        echo     "actions": [
        echo         { "command": { "action": "copy", "singleLine": false }, "keys": "ctrl+c" },
        echo         { "command": "paste", "keys": "ctrl+v" }
        echo     ]
        echo } > "%TEMP%\\wt_temp.json"

        type "%TEMP%\\wt_temp.json" >> %WT_SETTINGS%
        del "%TEMP%\\wt_temp.json" >nul
        echo Успешно: Настройки Windows Terminal обновлены
    )
)

:: Установка переменных окружения для разработки
setx LANG "ru_RU.UTF-8" >nul
setx LC_ALL "ru_RU.UTF-8" >nul
setx LC_CTYPE "ru_RU.UTF-8" >nul

:: Создание ярлыка для быстрого доступа к настройкам
set SHORTCUT_PATH="%USERPROFILE%\\Desktop\\UTF-8 Configuration.lnk"

if not exist %SHORTCUT_PATH% (
    echo Создание ярлыка на рабочем столе...
    set SCRIPT_PATH="%~f0"
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(%SHORTCUT_PATH%); $s.TargetPath = %SCRIPT_PATH%; $s.Description = 'Настройка UTF-8 для Windows'; $s.IconLocation = 'C:\\Windows\\System32\\control.exe,0'; $s.Save()" >nul 2>&1
)

:: Завершение
echo.
echo ==============================================================================
echo УСТАНОВКА ЗАВЕРШЕНА
echo.
echo Рекомендуется перезагрузить компьютер для применения всех изменений
echo.
echo Особенности настройки:
echo - Поддержка кириллицы в путях и именах файлов
echo - UTF-8 кодировка по умолчанию для консоли
echo - Совместимость с Python, Git и другими инструментами
echo - Поддержка Windows 11 и современных терминалов
echo.
echo Для проверки настроек после перезагрузки выполните:
echo chcp
echo echo %LANG%
echo python -c "import sys; print(sys.stdout.encoding)"
echo.
pause
