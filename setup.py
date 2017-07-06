import os
from setuptools import setup


def getSubpackages(name):
    """获取该模块下所有的子模块名称"""
    splist = []

    for dirpath, _dirnames, _filenames in os.walk(name):
        if os.path.isfile(os.path.join(dirpath, '__init__.py')):
            splist.append(".".join(dirpath.split(os.sep)))

    return splist


setup(
    name='redtorch',
    version='0.1.0',
    description='A framework for developing Quantitative Trading programmes',
    author='sun0x00',
    author_email='sun0x00@gmail.com',
    copyright='Copyright (c) 2017 sun0x00',
    url='https://github.com/sun0x00/redtorch',
    download_url='https://github.com/sheriferson/simplestatistics/tarball/0.2.5',
    keywords='quant quantitative investment trading algotrading',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 8',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows Server 2008',
        'Operating System :: Microsoft :: Windows :: Windows Server 2012',
        'Operating System :: Microsoft :: Windows :: Windows Server 2016',
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
                       '*.dat', '*.ini', '*.pfx', '*.scc', '*.crt', '*.key']}
)
