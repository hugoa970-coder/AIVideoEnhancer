@echo off
chcp 65001 > nul
title Subir AIVideoEnhancer a GitHub
cd /d "D:\Proyectos\AIVideoEnhancer"

echo ================================================================================
echo               SUBIENDO AIVideoEnhancer A TU REPOSITORIO GITHUB
echo ================================================================================
echo.

git remote remove origin 2>nul
git remote add origin https://github.com/hugoa970-coder/AIVideoEnhancer.git
git branch -M main

echo Conectando con https://github.com/hugoa970-coder/AIVideoEnhancer.git ...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo  [OK] Repositorio subido exitosamente con todas las protecciones legales.
    echo  URL: https://github.com/hugoa970-coder/AIVideoEnhancer
    echo ================================================================================
) else (
    echo.
    echo ================================================================================
    echo  [AVISO] Si el repositorio aún no existe en tu cuenta de GitHub:
    echo  1. Ve a tu navegador a: https://github.com/new
    echo  2. Escribe como Repository name: AIVideoEnhancer
    echo  3. Dejalo en Public y NO marques 'Add README' ni 'Add .gitignore'
    echo  4. Clic en "Create repository"
    echo  5. Vuelve a ejecutar este archivo (subir_github.bat)
    echo ================================================================================
)

pause
