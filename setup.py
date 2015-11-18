from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='kidraw',
    version='2',
    description='Construct Kicad schematic and footprint libraries programmatically',
    long_description=long_description,
    url='https://github.com/danderson/kidraw',
    author='David Anderson',
    author_email='dave@natulte.net',
    license='Apache License 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        
    ],
    keywords='electronics kicad schematic footprint',

    packages=find_packages(exclude=['contrib', 'docs', 'examples', 'tests']),
)
