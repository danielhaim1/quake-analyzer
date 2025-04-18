# Quake Analyzer

A Python CLI tool to fetch, analyze, and visualize global earthquake data from the [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/). Useful for identifying recurrence intervals, regional clusters, and year-by-year magnitude trends.

---

## Dependencies
This project relies on the following major Python libraries:
- [pandas](https://pandas.pydata.org/) for data manipulation and analysis.
- [requests](https://requests.readthedocs.io/en/latest/) for fetching data from the USGS API.
- [matplotlib](https://matplotlib.org/) for plotting data (optional, used with the `--plot` flag).

See `requirements.txt` for a full list of dependencies.

---

## Features

- Fetch earthquake data from USGS (up to 20 years back)
- Filter by magnitude, location, or radius
- Analyze recurrence intervals for major quakes (≥ 6.0)
- Output quake frequency by year
- Optional CSV export and bar chart plotting

---

## Installation

```bash
git clone https://github.com/danielhaim1/quake-analyzer.git
cd quake-analyzer
pip install -e .
```

---

## License
This project is licensed under the terms of the license specified in the `LICENSE.txt` file.

---

## Example Commands
Each example below shows how to use quake-analyzer and what kind of analysis you get.

### Example 1: Global major quakes (last 20 years)
This command analyzes global earthquakes of magnitude ≥ 6.0 over the past 20 years (7300 days). It reports the number of major quakes per year and estimates the average recurrence interval.

```bash
quake-analyzer --fetch --minmag 6.0 --days 7300
```

```bash
Fetched 2000 quakes

=== MAJOR EARTHQUAKE ANALYSIS ===
Total major quakes (≥ 6.0): 2000
Years: [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
Gaps between events: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
Average recurrence interval: 1.0 years

=== QUAKES PER YEAR ===
Date
2011    206
2012    133
2013    142
2014    155
2015    146
2016    147
2017    111
2018    134
2019    145
2020    121
2021    157
2022    127
2023    147
2024     99
2025     30
```

## CLI Options

| Argument        | Description                                                |
|----------------|------------------------------------------------------------|
| `--fetch`       | Fetch quake data from USGS                                |
| `--data`        | Pass custom quake list as a Python-style list             |
| `--minmag`      | Minimum magnitude to filter and analyze (default: 6.0)    |
| `--days`        | Number of days to look back for USGS fetch                |
| `--lat`         | Latitude for regional filter                              |
| `--lon`         | Longitude for regional filter                             |
| `--radius`      | Radius (in km) around lat/lon for regional filter         |
| `--export`      | Export filtered quakes to CSV                             |
| `--plot`        | Plot quake frequency per year (requires matplotlib)       |

### Example 2: Export results to CSV
```bash
quake-analyzer --fetch --minmag 6.0 --days 7300 --export
```

```bash
Fetched 2000 quakes

=== MAJOR EARTHQUAKE ANALYSIS ===
Total major quakes (≥ 6.0): 2000
Years: [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
Gaps between events: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
Average recurrence interval: 1.0 years

=== QUAKES PER YEAR ===
Date
2011    206
2012    133
2013    142
2014    155
2015    146
2016    147
2017    111
2018    134
2019    145
2020    121
2021    157
2022    127
2023    147
2024     99
2025     30

Exported 2000 major quakes to 'major_quakes_2025-04-18_10-34-46.csv' at 2025-04-18T10:34:46.478832
```

![Exported CSV Screenshot](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/example-2-export-to-csv.png?raw=true)

### Example 3: Filter by region (Japan, last 10 years)
This filters earthquakes within a 500 km radius of central Japan (Lat: 36.2048, Lon: 138.2529) over the past 10 years, and analyzes quakes with a magnitude of 5.5 or higher.

```bash
quake-analyzer --fetch --minmag 5.5 --days 3650 --lat 36.2048 --lon 138.2529 --radius 500
```

```bash
Fetched 78 quakes

=== MAJOR EARTHQUAKE ANALYSIS ===
Total major quakes (≥ 5.5): 78
Years: [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
Gaps between events: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
Average recurrence interval: 1.0 years

=== QUAKES PER YEAR ===
Date
2015     1
2016    10
2017     4
2018     8
2019     5
2020     8
2021    13
2022     9
2023     6
2024    13
2025     1
```

### Example 4: Regional quake history with plot
This fetches earthquakes of magnitude ≥ 3.0 from the past 20 years, within a 300 km radius around Northern California (lat 38.0, lon -122.0). It visualizes the yearly quake count as a bar chart.

```bash
quake-analyzer --fetch --minmag 3.0 --days 7300 --lat 38.0 --lon -122.0 --radius 300 --plot
```

```bash
Fetched 2000 quakes

=== MAJOR EARTHQUAKE ANALYSIS ===
Total major quakes (≥ 3.0): 2000
Years: [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
Gaps between events: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
Average recurrence interval: 1.0 years

=== QUAKES PER YEAR ===
Date
2005     14
2006    110
2007     96
2008    133
2009     84
2010    107
2011    145
2012     69
2013    105
2014     82
2015     79
2016    107
2017    104
2018     70
2019     77
2020    123
2021    170
2022     77
2023    101
2024    115
2025     32
```

![Regional Quakes Plot](https://github.com/danielhaim1/quake-analyzer/blob/master/docs/example-4-plot.png?raw=true)

---

## Releasing a New Version

This project uses `setuptools_scm` to derive the version number from Git tags and GitHub Actions to automate publishing to PyPI.

To release a new version:

1.  **Ensure Clean State:** Make sure your main branch (`master`) is up-to-date and all changes for the release are committed. Check `git status`.
2.  **Determine Version:** Decide on the new version number (e.g., `0.1.5`, `0.2.0`) following [Semantic Versioning](https://semver.org/).
3.  **Create Tag:** Create an annotated Git tag for the release commit:
    ```bash
    # Replace X.Y.Z with the new version
    git tag -a vX.Y.Z -m "Release version X.Y.Z"
    ```
4.  **Push Tag:** Push the tag to GitHub:
    ```bash
    # Replace vX.Y.Z with the tag you created
    git push origin vX.Y.Z
    ```
5.  **Create GitHub Release:**
    *   Go to the [Releases page](https://github.com/danielhaim1/quake-analyzer/releases) on GitHub.
    *   Click "Draft a new release".
    *   Choose the tag you just pushed (e.g., `vX.Y.Z`) from the dropdown.
    *   Set the "Release title" (usually the same as the tag).
    *   Write release notes describing the changes in this version (you can use "Auto-generate release notes").
    *   Click "**Publish release**".

Publishing the release on GitHub will automatically trigger the `publish.yml` workflow, which builds the package (using the version from the tag) and uploads it to PyPI. You can monitor the workflow run under the "Actions" tab in the GitHub repository.

---

## Notes

- USGS limits results to 20 years and 2000 entries per request.
- For smaller magnitudes (e.g., 3.0+), results may be capped quickly, especially in active zones.
- Timestamp columns in exported CSVs include both quake time and export time.
- Plots require `matplotlib`. Install via:

```bash
pip install matplotlib
```

