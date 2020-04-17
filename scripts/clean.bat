@echo off
for /d /r . %%i in (__pycache__) do @if exist "%%i" rd /s /q "%%i" && echo Removed "%%i"
for /d /r . %%i in (.mypy_cache) do @if exist "%%i" rd /s /q "%%i" && echo Removed "%%i"
for /d /r . %%i in (.pytest_cache) do @if exist "%%i" rd /s /q "%%i" && echo Removed "%%i"
for /d /r . %%i in (.coverage) do @if exist "%%i" del /s /q "%%i"
