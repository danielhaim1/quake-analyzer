from setuptools import setup, find_packages

setup(
    name="quake-analyzer",
    version="0.1.4",
    author="Daniel Haim",
    description="CLI tool for earthquake recurrence analysis using USGS data",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
        "importlib-resources; python_version < '3.9'",
    ],
    entry_points={
        "console_scripts": [
            "quake-analyzer = quake_analyzer.cli:main",
        ],
    },
    python_requires=">=3.7",
)
