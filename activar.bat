@echo off
chcp 65001 > nul
title AI Video & Audio Post-Production Enhancer (Patent US 2026/0341309 A1)
cd /d "D:\Proyectos\AIVideoEnhancer"
python run.py %*
pause
