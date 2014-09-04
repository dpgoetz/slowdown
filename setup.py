from setuptools import setup, find_packages

from slowdown import __version__ as version


name = 'slowdown'


setup(
    name=name,
    version=version,
    description='Slowdown Middleware',
    license='Apache License (2.0)',
    author='OpenStack, LLC.',
    author_email='david.goetz@rackspace.com',
    url='https://github.com/dpgoetz/slowdown',
    packages=find_packages(),
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Environment :: No Input/Output (Daemon)',
        ],
    install_requires=[],  # removed for better compat
    scripts=[],
    entry_points={
        'paste.filter_factory': [
            'slowdown=slowdown.slowdown:filter_factory',
            ],
        },
    )
