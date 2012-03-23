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
        'Framework :: Django',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Debuggers',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
    ],
    description='A watchdog for Gunicorn that interrupts long running requests.',
    download_url='https://bitbucket.org/evzijst/interruptingcow/downloads/interruptingcow-0.1.tar.gz',
    keywords='gunicorn debug watchdog interrupt',
    license='GNU LGPL',
    long_description=long_description(),
    name='interruptingcow',
    packages=['interruptingcow'],
    url='https://bitbucket.org/evzijst/interruptingcow',
    version='0.1',
)
