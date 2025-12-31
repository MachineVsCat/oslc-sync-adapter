from setuptools import setup, find_packages

setup(
    name="oslc-sync-adapter",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0.1",
        "lxml>=4.9.3",
    ],
    entry_points={
        "console_scripts": [
            "oslc-sync=cli:main",
        ],
    },
    author="mamonet",
    description="OSLC-based synchronization adapter for IBM ELM toolchain",
)
