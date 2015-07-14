# -*-coding:utf8-*-
from setuptools import setup, find_packages


print(find_packages())

setup(
    name='okpy',
    version='0.0.6',
    description='OK.py, a simple and rough test tool.',
    author='drz',
    url='https://github.com/drzunny/ok.py',
    license='Apache',
    platforms='any',
    install_requires=['colorama>=0.3.3'],
    scripts=['okpy.py']
)
