@echo off
title Auto-Stock

cd /d %~dp0
call venv\Scripts\activate

python -m src.app

pause