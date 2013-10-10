#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='smartfocus',
    version='1.0.0',
    packages=find_packages(exclude='tests'),
    url='http://github.com/mrichman/smartfocus',
    license='LICENSE.txt',
    author='Mark Richman',
    author_email='mark@markrichman.com',
    description='SmartFocus Campaign Commander REST Interface Client',
    install_requires=['poster>=0.8.1','requests >= 1.2.3']
)