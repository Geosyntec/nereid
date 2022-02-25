import re

from setuptools import setup

with open("nereid/nereid/__init__.py", encoding="utf8") as f:
    content = f.read()
    version = re.search(r'__version__ = "(.*?)"', content).group(1)
    author = re.search(r'__author__ = "(.*?)"', content).group(1)
    author_email = re.search(r'__email__ = "(.*?)"', content).group(1)


setup(version=version, author=author, author_email=author_email)
