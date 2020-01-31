del /S *.pyc
for /d /r %%i in (*__pycache__*) do rmdir /s /q "%%i" echo Removed "%%i"
for /d /r %%i in (*.mypy_cache*) do rmdir /s /q "%%i" echo Removed "%%i"
for /d /r %%i in (*.pytest_cache*) do rmdir /s /q "%%i" echo Removed "%%i"
