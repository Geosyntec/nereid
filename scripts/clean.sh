find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
rm -rf "*.mypy_cache*"
rm -rf "*.pytest_cache*"
