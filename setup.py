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
        "python-dotenv>=0.14,<0.15",
        "scipy>=1.5,<1.6",
        "pandas>=1.1,<1.2",
        "networkx>=2.5,<2.6",
        "pydot>=1.4,<1.5",
        "graphviz",
        "matplotlib>=3.3,<3.4",
        "fastapi>=0.61,<0.62",
        "pydantic>=1.7,<1.8",
        "aiofiles>=0.6,<0.7",
        "celery>=5.0,<5.1",
        "jinja2>=2.11,<2.12",
        "redis>=3.5,<3.6",
        "orjson>=3.4,<3.5",
        "pyyaml>=5.3,<5.4",
        "pint>=0.16,<0.17",
        "typing-extensions>=3.7,<3.8",
    ],
)
