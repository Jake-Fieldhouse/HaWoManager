from setuptools import setup, find_packages

setup(
    name='HaWoManager',
    version='0.0.1',
    description='Device management utilities with Home Assistant integration',
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests"],
)
