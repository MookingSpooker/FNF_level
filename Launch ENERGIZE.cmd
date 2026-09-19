@echo off
setlocal
set "FNF_GAME=%USERPROFILE%\Downloads\funkin-windows-64bit"
if exist "%~dp0game\Funkin.exe" set "FNF_GAME=%~dp0game"
if not exist "%FNF_GAME%\Funkin.exe" (
  echo Game not found. Use tools\Install-Mod.ps1 -GamePath "your game folder".
  pause
  exit /b 1
)
if not exist "%FNF_GAME%\mods\energize\_polymod_meta.json" (
  echo ENERGIZE is not installed. Use tools\Install-Mod.ps1 first.
  pause
  exit /b 1
)
echo Open Freeplay and choose Energize, or Story Mode and choose ENERGIZE: VS VOLT.
start "" /D "%FNF_GAME%" "%FNF_GAME%\Funkin.exe"
