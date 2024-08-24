@echo off
timeout 0 2>nul >nul
if errorlevel 1 (
    pbcopy
) else (
    pbpaste
)
