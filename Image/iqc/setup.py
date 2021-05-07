#!/usr/bin/env python3

from setuptools import setup, find_packages

def _read(path):
    with open(path, 'r') as f:
        return f.read()

setup (
	name ='iqc',
	version=0.8,
	license='MIT',
	description='IQC is an automation tool for checking image folder contents against inventories, verifying checksums, and checking metadata.',
	long_description=_read('README.md'),
	url='https://github.com/nulib/nul-rdc-scripts',
	author='Joshua Yocum',
	packages={'iqc'},
#    package_data={'dpx2ffv1': ['data/mediaconch_policies/*.xml']},
#    include_package_data=True,
    entry_points={'console_scripts': ['iqc = iqc.iqc:iqc_main'],},
	install_requires=[
		'pandas',
		'Pillow'
	],
    python_requires='>=3.6'
)
