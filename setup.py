from setuptools import setup, find_packages
import py2exe
import sys

setup(
    name='Log Checker',
    version='0.1',
    packages=find_packages(),


    console=['main.py'],  # Replace 'example.py' with your script name
    options={
        'py2exe': {
            'bundle_files': 3,  # Required for Python 3.12+
            'compressed': True,
        }
    },
    zipfile=None,


    install_requires=[
        # List your dependencies here
        'numpy',
        'pandas',
        'pyQT5',
    ],
    entry_points={
        'console_scripts': [
            'log_checker=main:main',  # Adjust this to your main function
        ],
    },
    author='Sam Gao',
    author_email='sam.gao@sharkninja.com',
    description='A tool for checking and analyzing logs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/log_checker',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
