@echo off
REM Script for repo restructure to monorepo style (Windows CMD adaptation)

echo 🔄 Starting refactor...

REM Create new structure
if not exist apps mkdir apps
if not exist libs mkdir libs
if not exist docs mkdir docs
if not exist tools mkdir tools
if not exist config mkdir config
if not exist internal mkdir internal

REM 1. Move modules to apps/
echo 📦 Moving modules to apps/...
for /d %%d in (02_MODULES\*) do (
    git mv "%%d" "apps\%%~nxd"
)

REM 2. Consolidate docs
echo 📚 Consolidating docs...
robocopy 05_DOCUMENTATION docs /move /e
robocopy cognitive-architect-manifesto docs\methodology /move /e
robocopy 01_ARCHITECTURE docs\architecture /move /e
robocopy 03_CASES docs\cases /move /e
robocopy 08_EVIDENCE docs\evidence /move /e

REM 3. Tools
echo 🔧 Moving tools...
robocopy 07_TOOLS tools /move /e

REM 4. Internal
echo ⚙️ Moving internal...
robocopy 09_META internal /move /e
robocopy 06_GRANT grants /move /e

REM 5. Remove empty dirs (manual rmdir if needed)
echo 🧹 Removing empty folders...
rmdir /s /q 01_ARCHITECTURE 2>nul
rmdir /s /q 02_MODULES 2>nul
rmdir /s /q 03_CASES 2>nul
rmdir /s /q 05_DOCUMENTATION 2>nul
rmdir /s /q 06_GRANT 2>nul
rmdir /s /q 07_TOOLS 2>nul
rmdir /s /q 08_EVIDENCE 2>nul
rmdir /s /q 09_META 2>nul
rmdir /s /q cognitive-architect-manifesto 2>nul

REM 6. Trash
echo 🗑️ Removing trash...
rmdir /s /q .idea 2>nul
rmdir /s /q Lib 2>nul
rmdir /s /q logs 2>nul
rmdir /s /q monitoring 2>nul

echo ✅ Refactor complete! Run git status.

