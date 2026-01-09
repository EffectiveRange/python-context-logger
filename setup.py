from setuptools import setup

setup(
    name='python-context-logger',
    description='Contextual structured logging library for Python',
    author='Ferenc Nandor Janky & Attila Gombos',
    author_email='info@effective-range.com',
    packages=['context_logger'],
    package_data={'context_logger': ['py.typed']},
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=['structlog']
)
