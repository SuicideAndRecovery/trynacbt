'''
License:
    Copyright (c) 2020 SuicideAndRecovery
    This code is licensed to you under an open source license (MIT/X11).
    See the LICENSE file for details.
'''
from setuptools import setup, find_packages

setup(
    name='trynacbt',
    version='0.0.1',
    description='TODO',  # TODO: Finish
    long_description='TODO',  # TODO: Finish
    url='https://github.com/SuicideAndRecovery/trynacbt',
    author='SuicideAndRecovery',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='',  # TODO: Keywords
    packages=find_packages(),
    install_requires=[
        'appdirs',
        'click',
        'python-dateutil',
        'requests',
        'scrapy==2.3',
        'tensorflow',
        'tensorflow_hub'
    ],
    entry_points='''
        [console_scripts]
        trynacbt=trynacbt.console:main
    '''
)
