"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
import setuptools
setuptools.setup(
    name="datefinder-dnl-extension",  # Replace with your own username
    version="0.0.1",
    author="DNL",
    author_email="info@dnl.com",
    description="Extension of the datefinderpackage for DNL",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
