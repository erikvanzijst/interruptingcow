#!/usr/bin/env python
# Installs django_alarma.

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
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Utilities',
    ],
    description='A Django middleware that interrupts long running requests.',
    download_url='https://bitbucket.org/evzijst/django_alarma/downloads/django_alarma-0.1.tar.gz',
    keywords='django debug watchdog middleware interrupt',
    license='GNU LGPL',
    long_description=long_description(),
    name='django_alarma',
    packages=['django_alarma'],
    url='https://bitbucket.org/evzijst/django_alarma',
    version='0.1',
)
