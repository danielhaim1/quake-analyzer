# Changelog
All notable changes to this project will be documented in this file.

## [0.0.2] - 2025-04-18 - Added location filtering

### Added
- Added location filtering by city, state, or country.
- Added radius filtering.
- Added export to CSV.
- Added plot of quake frequency per year.

## [0.0.1] - 2025-04-18 - Initial release

### Added
- Initial release of `quake-analyzer`.
- Core functionality to fetch, filter (magnitude, region), analyze (recurrence, frequency), and export (CSV) earthquake data from USGS.
- CLI interface with various command-line options.
- Optional plotting of quake frequency per year using Matplotlib.
- Basic project structure, README, LICENSE (MIT).
- Setup for packaging using `pyproject.toml` and `setup.py`.
- GitHub Actions for CI (linting) and automated PyPI publishing on release.