from setuptools import setup, find_packages

setup(
    name='HaWoManager',
    version='0.0.9',
    description='Device management utilities with Home Assistant integration',
    packages=find_packages(include=[
        "womgr",
        "custom_components",
        "custom_components.*",
    ]),
    include_package_data=True,


    install_requires=[],
main
)
