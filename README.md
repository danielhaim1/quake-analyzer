# Quake Analyzer

[![License](https://img.shields.io/github/license/danielhaim1/quake-analyzer.svg)](https://github.com/danielhaim1/quake-analyzer/blob/master/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/quake-analyzer.svg)](https://pypi.org/project/quake-analyzer/)
[![PyPI Version](https://img.shields.io/pypi/v/quake-analyzer.svg)](https://pypi.org/project/quake-analyzer/)

quake-analyzer is a command-line tool that fetches and analyzes earthquake data, including filtering based on magnitude and location, calculating recurrence intervals, and generating reports. This tool can help researchers and enthusiasts analyze earthquake data from the [USGS database](https://earthquake.usgs.gov/fdsnws/event/1/) over various timeframes.

![Quake Analyzer Screenshot](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/quake-analyzer.png?raw=true)

---

## Features
- Fetch earthquake data from the USGS Earthquake API.
- Filter earthquakes based on magnitude and region.
- Analyze major earthquakes and their recurrence intervals.
- Export the list to CSV.
- Plot the count of major earthquakes per year.
- Estimate the recurrence interval and probability of future major earthquakes.

---

## Installation

```bash
git clone https://github.com/danielhaim1/quake-analyzer.git
cd quake-analyzer
pip install -e .
```

## Dependencies
This project relies on the following major Python libraries:
- [pandas](https://pandas.pydata.org/) for data manipulation and analysis.
- [requests](https://requests.readthedocs.io/en/latest/) for fetching data from the USGS API.
- [matplotlib](https://matplotlib.org/) for plotting data (optional, used with the `--plot` flag).

---

## Options

| Option       | Description                                                                                 | Default          |
|--------------|---------------------------------------------------------------------------------------------|------------------|
| `--data`     | Manually pass quakes as `[[timestamp, magnitude, location], ...]`                          | None             |
| `--fetch`    | Fetch recent earthquakes from USGS                                                         | None             |
| `--minmag`   | Minimum magnitude to filter                                                                | `6.0`            |
| `--days`     | Number of days to look back from today                                                     | `1825` (5 years) |
| `--location` | Location name to filter by (supports city, state, or country from CSVs)                   | None             |
| `--radius`   | Radius in kilometers around the specified location                                         | None             |
| `--export`   | Export results to CSV                                                                      | Off              |
| `--plot`     | Plot earthquakes per year                                                                   | Off              |
| `--estimate`     | Estimate the recurrence interval and probability of major quakes | Off              |

---

## Examples

### Global major quakes in past 20 years
```bash
quake-analyzer --fetch --minmag 6.0 --days 7300
```

### Estimate Next Quake

```bash
quake-analyzer --fetch --minmag 6.0 --days 7300 --estimate
```

### Estimate Analysis (Colombia)
```bash
quake-analyzer --fetch --minmag 9.5 --location "Colombia" --radius 1000 --days 10000
quake-analyzer --fetch --minmag 8.5 --location "Colombia" --radius 1000 --days 10000
quake-analyzer --fetch --minmag 7.5 --location "Colombia" --radius 1000 --days 10000
```

### Location based filtering
```bash
# Quakes near Tokyo (within 300 km)
quake-analyzer --fetch --location "Tokyo" --radius 300 --minmag 5.5 --days 3650

# California region, major quakes (last 20 years)
quake-analyzer --fetch --location "California" --radius 500 --minmag 6.0 --days 7300

# Chile, strong events only
quake-analyzer --fetch --location "Chile" --radius 400 --minmag 6.8 --days 7300
```

### Custom manual input
```bash
# Manually analyze a couple of events
quake-analyzer --data "[['2021-12-01T12:00:00', 6.5, 'Tokyo'], ['2022-01-01T15:00:00', 7.0, 'Santiago']]"
```

### Export and Plot
```bash
# Export filtered results to CSV
quake-analyzer --fetch --location "Alaska" --radius 500 --minmag 6.0 --days 3650 --export

# Plot quake frequency per year
quake-analyzer --fetch --location "Indonesia" --radius 500 --minmag 6.0 --days 7300 --plot

# Export and plot together
quake-analyzer --fetch --location "Mexico" --radius 300 --minmag 6.2 --days 5000 --export --plot
```
---

## Location Resolution
You can pass `--location` using names of:
- Cities (e.g., `Tokyo`, `San Francisco`)
- States (e.g., `California`, `Bavaria`)
- Countries (e.g., `Japan`, `Mexico`)

Coordinates are looked up from:
```
src/data/
├── cities.csv
├── states.csv
├── countries.csv
```
Each file should include:
```csv
name,latitude,longitude
```
---

## Estimate: How It Works
The estimation feature calculates two important metrics based on recent earthquake data:
- Recurrence Interval: The average time (in years) between major earthquakes (≥ 6.0 magnitude).
- Probability: The likelihood of a major earthquake occurring within the next year.

### Calculation Process::
- Filter Major Quakes: Only earthquakes with a magnitude of 6.0 or higher are considered.
- Calculate Time Intervals: The tool calculates the time differences between each consecutive major earthquake.
- Compute Mean Recurrence Interval: The mean recurrence interval is the average of these time intervals.
- Estimate Probability: The probability of a major earthquake occurring within the next year is estimated as the inverse of the mean recurrence interval (1 / mean recurrence interval).

Example:
```bash
quake-analyzer --fetch --location "Tokyo" --radius 300 --minmag 9.5 --days 20000 --estimate
quake-analyzer --fetch --location "Tokyo" --radius 300 --minmag 8.5 --days 20000 --estimate
quake-analyzer --fetch --location "Tokyo" --radius 300 --minmag 7.5 --days 20000 --estimate
```

- Fetch earthquake data for Tokyo (within a 300 km radius).
- Filter by magnitude ≥ 6.0.
- Estimate the recurrence interval and probability based on the quakes in that region over the last 10 years (3650 days).

---

## Outputs
The tool will output earthquake data in the terminal, including:

- The total number of major earthquakes.
- The years in which earthquakes occurred.
- Gaps between major earthquakes.
- A summary of earthquakes per year.
- Estimates of recurrence intervals and probabilities (if --estimate is used).

- If `--export` is used, the results will be saved to a CSV file with the following columns:
- Years Ago
- Magnitude
- Date
- Timestamp
- Location
- Type (Major or Moderate)
- Mean Recurrence Interval (years)
- Estimated Probability (per year)

---

## Screenshots

![Quake Analyzer Screenshot (Estimate)](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/img-10.png?raw=true)
![Quake Analyzer Screenshot (Estimate)](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/img-9.png?raw=true)
![Quake Analyzer Screenshot (Estimate)](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/img-8.png?raw=true)
![Quake Analyzer Screenshot (Estimate)](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/img-7.png?raw=true)
![Quake Analyzer Screenshot](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/img-1.png?raw=true)
![Quake Analyzer Screenshot](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/img-2.png?raw=true)
![Quake Analyzer Screenshot](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/img-3.png?raw=true)
![Quake Analyzer Screenshot](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/img-4.png?raw=true)
![Quake Analyzer Screenshot](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/img-5.png?raw=true)

---

## Notes

- USGS limits results to 20 years and 2000 entries per request.
- For smaller magnitudes (e.g., 3.0+), results may be capped quickly, especially in active zones.
- Timestamp columns in exported CSVs include both quake time and export time.
- Plots require `matplotlib`. Install via:

```bash
pip install matplotlib
```

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## Reporting Bugs
If you encounter a bug or issue, please open an issue on the [GitHub repository](https://github.com/danielhaim1/quake-analyzer/issues) with as much detail as possible including:
- Command used
- Stack trace or error message
- Your OS and Python version