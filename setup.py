import re

from setuptools import setup

with open("nereid/nereid/__init__.py", encoding="utf8") as f:
    content = f.read()
    version = re.search(r'__version__ = "(.*?)"', content).group(1)
    author = re.search(r'__author__ = "(.*?)"', content).group(1)
    author_email = re.search(r'__email__ = "(.*?)"', content).group(1)


setup(
    version=version,
    author=author,
    author_email=author_email,
    install_requires=[
        "python-dotenv>=0.14,<0.19",
        "scipy>=1.5,<1.8",
        "pandas>=1.1,<1.4",
        "networkx>=2.5,<2.6",
        "pydot>=1.4,<1.5",
        "graphviz",
        "matplotlib>=3.3,<3.5",
        "fastapi>=0.65.3,<0.66",
        "aiofiles>=0.6,<0.8",
        "celery>=5.0,<5.2",
        "jinja2>=2.11,<3.1",
        "redis>=3.5,<3.6",
        "orjson>=3.4,<3.6",
        "pyyaml>=5.4.1,<5.5",
        "pint>=0.16,<0.18",
    ],
)
