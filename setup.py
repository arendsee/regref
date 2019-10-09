from setuptools import setup

from regref.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="regref",
    version=__version__,
    description="Munge tables of data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arendsee/regref",
    author="Zebulun Arendsee",
    author_email="zbwrnz@gmail.com",
    packages=["regref"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["regref=regref.main:main"]},
    zip_safe=False,
)
