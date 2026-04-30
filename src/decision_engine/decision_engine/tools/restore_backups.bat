@echo off
:: Восстановление файлов из резервных копий
:: Этот скрипт позволяет восстановить файлы после конвертации кодировок

:: Настройка окружения
chcp 65001 >nul
cls
color 0e

echo ==============================================================================
echo ВОССТАНОВЛЕНИЕ ИЗ РЕЗЕРВНЫХ КОПИЙ
::
:: Внимание: Эта операция восстановит оригинальные файлы из резервных копий
:: Все изменения после конвертации кодировок будут потеряны
::
:: Скрипт найдет последнюю резервную копию и восстановит файлы
::
:: Версия: 1.0.0
:: Дата: %date%
echo ==============================================================================

echo.
:: Поиск директории backups
echo Поиск резервных копий...

if not exist "backups" (
    echo ОШИБКА: Директория backups не найдена
    echo Убедитесь, что вы находитесь в корне проекта
    echo Или создайте резервную копию с помощью scripts\\convert_to_utf8.py
    echo.
    pause
    exit /b 1
)

:: Поиск последней резервной копии
set LATEST_BACKUP=
pushd "backups" >nul

:: Сортировка по времени модификации, берем последнюю
for /f "delims=" %%i in ('dir /b /ad /o-d') do (
    if not defined LATEST_BACKUP (
        set LATEST_BACKUP=%%i
    )
)
popd >nul

if not defined LATEST_BACKUP (
    echo ОШИБКА: Не найдено ни одной резервной копии в директории backups
    echo Запустите сначала scripts\\convert_to_utf8.py для создания резервной копии
    echo.
    pause
    exit /b 1
)

echo Найдена последняя резервная копия: %LATEST_BACKUP%
set BACKUP_PATH="backups\\%LATEST_BACKUP%"

echo.
echo Резервная копия создана:
for /f "tokens=1-3" %%a in ('dir %BACKUP_PATH% ^| findstr "%%LATEST_BACKUP%%"') do (
    echo Дата: %%a Время: %%b
)

echo.
:: Предупреждение и подтверждение
echo ВНИМАНИЕ: ЭТА ОПЕРАЦИЯ ВОССТАНОВИТ ОРИГИНАЛЬНЫЕ ФАЙЛЫ
echo Все изменения после конвертации кодировок будут ПОТЕРЯНЫ
echo.

:confirm
set /p CONFIRM="Вы уверены, что хотите продолжить? (y/n): "
if /i "%CONFIRM%"=="y" goto start_restore
if /i "%CONFIRM%"=="yes" goto start_restore
echo Операция отменена
pause
exit /b 0

:start_restore
echo.
echo Начало восстановления файлов...
echo.

:: Создаем директорию для логов
if not exist "logs" mkdir "logs" >nul
set LOG_FILE="logs\\restore_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"
set LOG_FILE=%LOG_FILE: =0%

echo Восстановление из резервной копии: %LATEST_BACKUP% > %LOG_FILE%
echo Время начала: %date% %time% >> %LOG_FILE%
echo. >> %LOG_FILE%

set RESTORED_COUNT=0
set FAILED_COUNT=0
set TOTAL_COUNT=0

:: Восстановление файлов
for /r %BACKUP_PATH% %%f in (*) do (
    :: Вычисляем относительный путь
    set "FILE_PATH=%%f"
    set "RELATIVE_PATH=!FILE_PATH:%BACKUP_PATH%=%!"
    set "TARGET_FILE=!RELATIVE_PATH:~1!"

    :: Заменяем обратные слеши на прямые для корректной работы
    set "TARGET_FILE=!TARGET_FILE:\\\=/!"

    :: Выполняем восстановление в отдельном блоке для обработки переменных
    call :restore_single_file "%%f" "!TARGET_FILE!"
)

goto log_summary

:restore_single_file
set "SOURCE=%~1"
set "TARGET=%~2"
set /a TOTAL_COUNT+=1

:: Отладочная информация
>> %LOG_FILE% echo Источник: %SOURCE%
>> %LOG_FILE% echo Назначение: %TARGET%

:: Создаем родительскую директорию для целевого файла
for %%i in ("%TARGET%") do (
    if not "%%~dpi"=="" (
        if not exist "%%~dpi" mkdir "%%~dpi" >nul
    )
)

:: Копируем файл
copy "%SOURCE%" "%TARGET%" >nul 2>&1
if %errorlevel% == 0 (
    echo Восстановлено: %TARGET%
    echo [OK] %TARGET% >> %LOG_FILE%
    set /a RESTORED_COUNT+=1
) else (
    echo ОШИБКА: Не удалось восстановить %TARGET%
    echo [ERROR] %TARGET% >> %LOG_FILE%
    set /a FAILED_COUNT+=1
)

:: Задержка для корректной обработки переменных
ping 127.0.0.1 -n 1 >nul
exit /b

:log_summary
echo.
echo ==============================================================================
echo РЕЗУЛЬТАТЫ ВОССТАНОВЛЕНИЯ
echo.
echo Всего файлов обработано: %TOTAL_COUNT%
echo Успешно восстановлено: %RESTORED_COUNT%
echo Ошибок: %FAILED_COUNT%

echo.
echo Журнал операции сохранен в: %LOG_FILE%
echo.

:: Добавляем результаты в лог
>> %LOG_FILE% echo.
>> %LOG_FILE% echo Результаты:
>> %LOG_FILE% echo Всего файлов: %TOTAL_COUNT%
>> %LOG_FILE% echo Восстановлено: %RESTORED_COUNT%
>> %LOG_FILE% echo Ошибок: %FAILED_COUNT%
>> %LOG_FILE% echo Время окончания: %date% %time%

if %FAILED_COUNT% == 0 (
    echo [OK] Все файлы успешно восстановлены
    >> %LOG_FILE% echo Статус: УСПЕШНО
) else (
    echo [ERROR] Ошибки при восстановлении
    >> %LOG_FILE% echo Статус: ЧАСТИЧНО
)

echo Рекомендации:
echo - Проверьте целостность восстановленных файлов
echo - При необходимости создайте новую резервную копию
echo - После восстановления может потребоваться повторная настройка Git

echo.
pause
exit /b 0
