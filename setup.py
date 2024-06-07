from setuptools import setup

setup(
    name='python-context-logger',
    version='1.1.4',
    description='Contextual structured logging library for Python',
    author='Ferenc Nandor Janky & Attila Gombos',
    author_email='info@effective-range.com',
    packages=['context_logger'],
    package_data={'context_logger': ['py.typed']},
    install_requires=['structlog']
)
