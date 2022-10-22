import os

from setuptools import setup
from setuptools.config.setupcfg import read_configuration

# create home directory
if not os.path.isdir(os.path.join(os.environ['HOME'], '.solo_sis_loader')):
    os.mkdir(os.path.join(os.environ['HOME'], '.solo_sis_loader'))

extras = read_configuration('setup.cfg')['options']['extras_require']

setup(
    use_scm_version=True,
    extras_require=extras,
)
