import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tfutils", 
    version="0.0.1",
    author="Luca G. Cazzanti",
    author_email="luca@ieee.org",
    description="Tracab soccer data file utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gihub.com/lucacazzanti/tfutils",
    packages=setuptools.find_packages(),
    python_requires='>=3.9',
)