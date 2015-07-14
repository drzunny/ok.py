# -*-coding:utf8-*-
from setuptools import setup, find_packages

setup(
    name='okpy',
    version='0.1.0',
    description='OK.py, a simple and rough test tool.',
    author='drz',
    url='https://github.com/drzunny/ok.py',
    license='Apache',
    platforms='any',
    py_modules=['okpy'],
    entry_points={'console_scripts':['okpy=okpy:__okpy_entrypoint']},
    install_requires=['colorama>=0.3.3']
)
