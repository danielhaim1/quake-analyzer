# Changelog
All notable changes to this project will be documented in this file.

## [0.0.3] - [0.0.6] - 2025-04-18 - Added Recurrence Interval Estimation

#### Added
- Added estimate functionality for predicting the recurrence interval and probability of future major earthquakes (≥ 6.0 magnitude).
- Estimated the mean recurrence interval based on historical earthquake data.
- Calculated the estimated probability of a major earthquake occurring in the next year.
- Estimate output now included in the terminal results, providing a more thorough analysis.

#### Changed
- Enhanced output with estimated recurrence interval and probability if --estimate flag is used.
- Updated the command-line interface to include --estimate for automatic estimation of recurrence intervals.

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