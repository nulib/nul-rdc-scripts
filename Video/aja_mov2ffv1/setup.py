#!/usr/bin/env python3

from setuptools import setup
#with open("README") as f:
#	long_description = f.read()

setup (
	name ='aja_mov2ffv1',
	version='1.0',
	license='MIT',
#	long_description=long_description,
	author='Joshua Yocum',
	packages={'aja_mov2ffv1'},
    package_data={'aja_mov2ffv1': ['data/mediaconch_policies/*.xml']},
    include_package_data=True,
    entry_points={'console_scripts': ['aja-mov2ffv1 = aja_mov2ffv1.aja_mov2ffv1:main'],},
    python_requires='>=3.6'
)