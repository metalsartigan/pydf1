import setuptools
from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='df1',
    version='0.5',
    packages=setuptools.find_packages(),
    url='https://github.com/metalsartigan/pydf1',
    license='MIT License',
    author='Jerther',
    author_email='jtheriault@metalsartigan.com',
    description='A basic DF1 implementation in Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
