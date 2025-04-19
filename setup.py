from setuptools import setup, find_packages

setup(
    name="quake-analyzer",
    version="0.1.0",
    author="Daniel Haim",
    description="CLI tool for earthquake recurrence analysis using USGS data",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "quake_analyzer": ["data/*.csv"],
    },
    install_requires=[
        "pandas",
        "numpy",
        "requests",
        "matplotlib",
        "colorama",
    ],
    entry_points={
        "console_scripts": [
            "quake-analyzer = quake_analyzer.cli:main",
        ],
    },
    python_requires=">=3.7",
)
