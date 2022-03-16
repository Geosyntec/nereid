import re

from setuptools import setup


def search(substr: str, content: str):
    found = re.search(substr, content)
    if found:
        return found.group(1)
    return ""


with open("nereid/nereid/__init__.py", encoding="utf8") as f:
    content = f.read()
    version = search(r'__version__ = "(.*?)"', content)
    author = search(r'__author__ = "(.*?)"', content)
    author_email = search(r'__email__ = "(.*?)"', content)


setup(version=version, author=author, author_email=author_email)
