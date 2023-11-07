from setuptools import setup, find_packages

setup(
    name='fileIntegritySync',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'paramiko>=2.7.2',
        'pytest>=6.2.4',
    ],
    entry_points={
        'console_scripts': [
            'fileIntegritySync=fileIntegritySync:main',
        ],
    },
)
