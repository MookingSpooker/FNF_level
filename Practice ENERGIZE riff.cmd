@echo off
setlocal
set "FNF_GAME=%USERPROFILE%\Downloads\funkin-windows-64bit"
if exist "%~dp0game\Funkin.exe" set "FNF_GAME=%~dp0game"
if not exist "%FNF_GAME%\Funkin.exe" exit /b 1
if not exist "%~dp0dist\energize-practice-first.fnfc" exit /b 1
start "" /D "%FNF_GAME%" "%FNF_GAME%\Funkin.exe" --song "%~dp0dist\energize-practice-first.fnfc"
