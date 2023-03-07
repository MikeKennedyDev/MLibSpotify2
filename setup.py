# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# This call to setup() does all the work
setup(
    name="MLibSpotify2",
    version="1.0.0",
    description="Library for use in personal spotify account",
    long_description_content_type="text/markdown",
    author="MikeKennedyDev",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["MLibSpotify2"],
    install_requires=[
        'requests'
    ],
    include_package_data=True,
)