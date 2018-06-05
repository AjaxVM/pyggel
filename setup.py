
from setuptools import setup

with open('requirements.txt') as reqs:
    dependencies = [req.strip() for req in reqs]

print(dependencies)

setup(
    name = 'pyggel',
    version = '0.2.0',
    author = 'Matthew Roe',
    author_email = 'ajaxvm@gmail.com',
    maintainer = 'Matthew Roe',
    maintainer_email = 'ajaxvm@gmail.com',
    description = 'PYGGEL (PYthon Graphical Game Engine and Libraries)',
    license = 'MIT',
    keywords = 'game 3d opengl engine 2d',
    url = 'https://github.com/AjaxVM/pyggel',
    packages = ['pyggel'],
    long_description = open('README.md').read(),
    install_requires = dependencies
)
