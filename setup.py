#!/usr/bin/env python
# Installs interruptingcow.

import os, sys
from distutils.core import setup

def long_description():
    """Get the long description from the README"""
    return open(os.path.join(sys.path[0], 'README.rst')).read()

setup(
    author='Erik van Zijst',
    author_email='erik.van.zijst@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Debuggers',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
    ],
    description='A watchdog that interrupts long running code.',
    download_url='https://bitbucket.org/evzijst/interruptingcow/downloads/interruptingcow-0.7rc1.tar.gz',
    keywords='debug watchdog timer interrupt',
    license='MIT',
    long_description=long_description(),
    name='interruptingcow',
    packages=['interruptingcow'],
    url='https://bitbucket.org/evzijst/interruptingcow',
    version='0.7rc1',
)
