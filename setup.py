from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
package_name = 'kuddl'

def read_file(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

# imports __version__
exec(read_file(path.join(package_name, '_version.py')))

setup(
    name='kuddl',
    version=__version__,
    description='YAML+Python data description language',
    long_description=read_file('README.md'),
    url='https://github.com/ktbarrett/kuddl',
    author='Kaleb Barrett',
    author_email='dev.ktbarrett@gmail.com',
    license='MIT',
    packages=[package_name],
    python_requires='>=3.0',
    install_requires=['pyyaml'],
)
