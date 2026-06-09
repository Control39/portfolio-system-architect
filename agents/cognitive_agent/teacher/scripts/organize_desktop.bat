@echo off
REM Скрипт организации рабочего стола
echo Организация рабочего стола...

REM Создание папок
mkdir "Documents" 2>nul
mkdir "Projects" 2>nul
mkdir "Archives" 2>nul
mkdir "Installers" 2>nul
mkdir "Images" 2>nul
mkdir "Backups" 2>nul
mkdir "Temporary" 2>nul

echo Папки созданы
echo.
echo Перемещение файлов...

REM Перемещение по расширениям (пример)
REM move *.pdf "Documents" 2>nul
REM move *.doc* "Documents" 2>nul
REM move *.txt "Documents" 2>nul
REM move *.md "Documents" 2>nul

REM move *.png "Images" 2>nul
REM move *.jpg "Images" 2>nul
REM move *.jpeg "Images" 2>nul

REM move *.zip "Archives" 2>nul
REM move *.rar "Archives" 2>nul
REM move *.7z "Archives" 2>nul

REM move *.exe "Installers" 2>nul
REM move *.msi "Installers" 2>nul

echo.
echo Очистка временных файлов...
del *.tmp 2>nul
del ~*.* 2>nul

echo.
echo Готово! Рабочий стол организован.
pause
