@echo off
chcp 65001 > nul
python build_exe.py
exit /b %errorlevel%
