from setuptools import setup, find_packages

# Read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="quake-analyzer",
    version="0.1.1",
    description="CLI tool to fetch and analyze earthquake data from USGS",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/your_username/quake-analyzer",
    author="Daniel Haim",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas",
        "requests",
        "matplotlib"
    ],
    entry_points={
        "console_scripts": [
            "quake-analyzer=quake_analyzer.cli:main"
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
)
