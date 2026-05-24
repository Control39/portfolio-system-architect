@echo off
:: Настройка рабочего окружения для проекта cloud-reason
:: Этот скрипт устанавливает все необходимые настройки

:: Настройка окружения
chcp 65001 >nul
cls

color 0a

echo ==============================================================================
echo НАСТРОЙКА РАБОЧЕГО ОКРУЖЕНИЯ ДЛЯ CLOUD-REASON
::
:: Цель: Подготовка среды разработки для корректной работы с UTF-8 кодировкой
:: Особенности:
:: - Поддержка кириллицы в путях и именах файлов
:: - Совместимость с Windows 11
:: - Интеграция с VS Code, Git и Python
:: - Автоматическое резервное копирование
::
:: Версия: 1.0.0
:: Дата: %date%
echo ==============================================================================

echo.
echo Проверка наличия необходимых инструментов...

:: Проверка Python
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python найден
) else (
    echo [ERROR] Python не найден. Установите Python 3.8+
    set PYTHON_MISSING=true
)

:: Проверка Git
git --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Git найден
) else (
    echo [ERROR] Git не найден. Установите Git
    set GIT_MISSING=true
)

:: Проверка pip
pip --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] pip найден
) else (
    echo [WARNING] pip не найден. Попробуем установить зависимости через python -m pip
)

:: Проверка наличия директорий
if not exist "scripts" (
    echo [ERROR] Не найдена директория scripts
    mkdir scripts >nul
    echo [FIXED] Создана директория scripts
)

if not exist "configs" (
    echo [ERROR] Не найдена директория configs
    mkdir configs >nul
    echo [FIXED] Создана директория configs
)
)

if not exist "tools" (
    echo [ERROR] Не найдена директория tools
    mkdir tools >nul
    echo [FIXED] Создана директория tools
)

if not exist "docs" (
    echo [ERROR] Не найдена директория docs
    mkdir docs >nul
    echo [FIXED] Создана директория docs
)

if not exist "logs" (
    mkdir logs >nul
    echo [INFO] Создана директория logs для логов
)

if not exist "backups" (
    mkdir backups >nul
    echo [INFO] Создана директория backups для резервных копий
)

:: Установка зависимостей Python
echo.
echo Установка Python зависимостей...

if defined PYTHON_MISSING (
    echo Пропуск установки зависимостей: Python не установлен
) else (
    if exist "requirements.txt" (
        echo Найден requirements.txt
        pip install -r requirements.txt --upgrade
    ) else (
        echo Установка необходимых пакетов...
        pip install chardet --upgrade
        pip install colorama --upgrade
    )
)

:: Копирование конфигураций VS Code
echo.
echo Настройка VS Code...

if not exist ".vscode" (
    mkdir .vscode >nul
    echo [INFO] Создана директория .vscode
)

if exist "configs\\vscode_settings.json" (
    copy "configs\\vscode_settings.json" ".vscode\\settings.json" >nul
    echo [OK] Настройки VS Code скопированы
) else (
    echo [ERROR] Не найден configs\\vscode_settings.json
)

:: Проверка .gitignore
echo.
echo Проверка .gitignore...

if not exist ".gitignore" (
    echo Создание .gitignore...
    echo # Автогенерированные файлы >> .gitignore
    echo logs/ >> .gitignore
    echo backups/ >> .gitignore
    echo __pycache__/ >> .gitignore
    echo *.pyc >> .gitignore
    echo .vscode/ >> .gitignore
    echo *.log >> .gitignore
    echo .env >> .gitignore
    echo node_modules/ >> .gitignore
    echo *.bak >> .gitignore
    echo *.tmp >> .gitignore
    echo 
    echo # Системные файлы >> .gitignore
    echo Thumbs.db >> .gitignore
    echo .DS_Store >> .gitignore
    echo 
    echo # IDE >> .gitignore
    echo .idea/ >> .gitignore
    echo *.swp >> .gitignore
    echo *.swo >> .gitignore
    echo 
    echo [INFO] Создан .gitignore
) else (
    echo [OK] .gitignore найден
    
    :: Проверка на наличие важных правил
    findstr /c:"logs/" .gitignore >nul
    if %errorlevel% == 1 echo logs/ >> .gitignore
    
    findstr /c:"backups/" .gitignore >nul
    if %errorlevel% == 1 echo backups/ >> .gitignore
)

:: Настройка Git
echo.
echo Настройка Git...

if defined GIT_MISSING (
    echo Пропуск настройки Git: Git не установлен
) else (
    git config core.quotepath false
    git config core.autocrlf false
    git config commit.encoding utf-8
    
    echo [OK] Основные настройки Git применены
    
    :: Проверка .gitattributes
    if not exist ".gitattributes" (
        echo Создание .gitattributes...
        echo * text=auto >> .gitattributes
        echo *.py text eol=lf >> .gitattributes
        echo *.js text eol=lf >> .gitattributes
        echo *.html text eol=lf >> .gitattributes
        echo *.css text eol=lf >> .gitattributes
        echo *.md text eol=lf >> .gitattributes
        echo *.txt text eol=lf >> .gitattributes
        echo [INFO] Создан .gitattributes
    ) else (
        echo [OK] .gitattributes найден
    )
)

:: Проверка скриптов
echo.
echo Проверка скриптов...

call tools\\quick_check.bat

:: Завершение
echo.
echo ==============================================================================
echo НАСТРОЙКА ЗАВЕРШЕНА
echo.
echo Рекомендуемые действия:
echo 1. Перезагрузите компьютер для применения системных настроек
echo 2. Откройте проект в VS Code
echo 3. Запустите scripts\\analyze_all.py для анализа кодировок
echo 4. При необходимости запустите configs\\windows_env.bat от имени администратора
echo.
echo Особенности конфигурации:
echo - Поддержка кириллицы в путях и именах файлов
echo - UTF-8 кодировка по умолчанию для всех инструментов
echo - Автоматическое резервное копирование перед конвертацией
echo - Подробное логирование всех операций
echo - Совместимость с Windows 11 и современными терминалами
echo.

if defined PYTHON_MISSING (
    echo ВНИМАНИЕ: Python не установлен. Некоторые функции будут недоступны.
)

if defined GIT_MISSING (
    echo ВНИМАНИЕ: Git не установлен. Управление версиями будет ограничено.
)

echo Для быстрой проверки состояния среды запустите: tools\\quick_check.bat
echo.
pause