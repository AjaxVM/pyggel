
from setuptools import setup

# dependencies = [
#     'numpy>=1.14',
#     'Pillow>=5',
#     'pygame>=1.9',
#     'PyOpenGL>=3.1'
# ]

with open('requirements.txt') as reqs:
    dependencies = [req.strip() for req in reqs]

print(dependencies)

setup(
    name = 'pyggel',
    version = '0.2.0',
    author = 'Matthew Roe',
    description = 'PYGGEL (PYthon Graphical Game Engine and Libraries)',
    license = 'MIT',
    keywords = 'game 3d opengl engine 2d',
    url = 'https://github.com/AjaxVM/pyggel',
    packages = ['pyggel'],
    long_description = open('README.md').read(),
    install_requires = dependencies
)
