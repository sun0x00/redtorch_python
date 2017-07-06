# encoding: UTF-8

import os

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

def getSubpackages(name):
    """获取该模块下所有的子模块名称"""
    splist = []

    for dirpath, _dirnames, _filenames in os.walk(name):
        if os.path.isfile(os.path.join(dirpath, '__init__.py')):
            splist.append(".".join(dirpath.split(os.sep)))

    return splist

setup(
    name='redtorch',
    version='0.1.0a4',
    description='A framework for developing Quantitative Trading programmes',
    long_description=long_description,
    author='sun0x00',
    author_email='sun0x00@gmail.com',
    url='https://github.com/sun0x00/redtorch',
    keywords='quant quantitative investment trading algotrading',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 8',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows Server 2008',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business :: Financial :: Investment',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: MIT License'
    ],
    packages=getSubpackages('redtorch'),
    package_data={'': ['*.json', '*.md', '*.ico',
                       '*.h', '*.cpp', '*.bash', '*.txt',
                       '*.dll', '*.lib', '*.so', '*.pyd',
                       '*.dat', '*.ini', '*.pfx', '*.scc', '*.crt', '*.key']},
    install_requires=['vnpy'],
)
