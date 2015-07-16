# -*-coding:utf8-*-
from setuptools import setup, find_packages

setup(
    name='okpy',
    version='0.2.0',
    description='OK.py, a simple and rough test tool.',
    author='drz',
    url='https://github.com/drzunny/ok.py',
    license='Apache',
    platforms='any',
    packages=find_packages(),
    entry_points={'console_scripts':['okpy=okpy.main:okpy_main']},
    install_requires=['colorama>=0.3.3']
)
