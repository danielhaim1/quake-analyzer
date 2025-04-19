# Changelog
All notable changes to this project will be documented in this file.

## [0.1.2] - 2025-04-19 - Full CLI Packaging & Data Integration

### Added
- Fully working CLI command: `quake-analyzer` now available after install.
- Bundled `cities.csv`, `states.csv`, and `countries.csv` using `importlib.resources`.
- Added support for `importlib.resources.files()` to safely access package data.
- Added `data/` directory to package and included it via `pyproject.toml`.

### Changed
- Migrated project structure to modern `src/` layout (`src/quake_analyzer`).
- Updated `pyproject.toml` with `package-dir`, `package-data`, and `scripts` sections.
- Cleaned up `requirements.txt` and ensured reproducible local builds.
- Renamed version to `0.1.0` to mark milestone: first fully installable & publishable release.

### Fixed
- Fixed `ModuleNotFoundError` caused by missing `quake_analyzer` module after install.
- Fixed CSV path resolution errors during CLI execution by using correct data path lookups.

## [0.0.7] - 2025-04-18 - Bug Fixes and Plotting Enhancements

### Added
- Added checks to ensure that minmag is passed correctly when calling the recurrence interval estimation function (estimate_recurrence_interval()).
- Added graceful error handling for missing data when plotting earthquake frequency per year.
- Included a message indicating whether the estimated probability of a major earthquake is HIGH or LOW, based on the calculated recurrence interval.
- Enhanced the --plot functionality to only attempt plotting if there is valid data.

### Changed
- Fixed TypeError by ensuring minmag is always passed as an argument for estimate_recurrence_interval().
- Improved the error messages related to plotting when there is no data or matplotlib is not installed.
- Refined the logic for plotting earthquake frequencies to handle cases where the data is empty or unavailable.

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