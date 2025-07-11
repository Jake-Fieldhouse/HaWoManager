from setuptools import setup, find_packages

setup(
    name='HaWoManager',
    version='0.0.7',
    description='Device management utilities with Home Assistant integration',
    packages=find_packages(include=[
        "womgr",
        "custom_components",
        "custom_components.*",
    ]),
    include_package_data=True,
    install_requires=["requests"],
    entry_points={
        'console_scripts': [
            'womgr-cli=womgr_cli:main',
            'dashboard-cli=dashboard_cli:main',
        ]
    },
)
