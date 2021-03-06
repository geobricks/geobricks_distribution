from setuptools import setup
from setuptools import find_packages

setup(
    name='GeobricksDistribution',
    version='0.1.15',
    author='Simone Murzilli; Guido Barbaglia',
    author_email='geobrickspy@gmail.com',
    packages=find_packages(),
    license='LICENSE.txt',
    long_description=open('README.md').read(),
    description='Geobricks geospatial data distribution library.',
    install_requires=[
        'watchdog',
        'flask',
        'flask-cors',
        'GeobricksCommon',
        'GeobricksSpatialQuery',
        "GeobricksGISRaster",
        "GeobricksGISVector"
    ],
    url='http://pypi.python.org/pypi/GeobricksDistribution/',
    keywords=['geobricks', 'stats', 'geostats', 'zonalstats', 'gis', 'statistics', 'geostatistics']
)
