import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import ast
import requests
from colorama import Fore, init
import os
from importlib.resources import files

def get_data_path(filename):
    return files("quake_analyzer").joinpath("data", filename)

def load_places():
    def prep(filepath, name_col, source_name):
        print(Fore.WHITE + f"Loading {source_name}...")
        df = pd.read_csv(filepath)

        required = {name_col, "latitude", "longitude"}
        if not required.issubset(df.columns):
            print(Fore.YELLOW + f"Skipping {source_name}: missing columns {required - set(df.columns)}")
            return pd.DataFrame(columns=["name_lower", "latitude", "longitude"])

        df = df[[name_col, "latitude", "longitude"]].dropna()
        df["name_lower"] = df[name_col].str.strip().str.lower()
        return df

    cities = prep(get_data_path("cities.csv"), "name", "cities.csv")
    countries = prep(get_data_path("countries.csv"), "name", "countries.csv")
    states = prep(get_data_path("states.csv"), "name", "states.csv")

    return pd.concat([cities, states, countries], ignore_index=True)

PLACE_COORDS = load_places()

init(autoreset=True)


def get_location_coords(location_name):
    # Normalize the location name for matching
    location_name_lower = location_name.strip().lower()

    # Search for the location in the loaded PLACE_COORDS DataFrame
    location_data = PLACE_COORDS[PLACE_COORDS["name_lower"] == location_name_lower]
    if not location_data.empty:
        # Return the first match (could be extended to handle multiple locations)
        lat = location_data.iloc[0]["latitude"]
        lon = location_data.iloc[0]["longitude"]
        return lat, lon
    else:
        print(Fore.RED + f"Location '{location_name}' not found in available data.")
        return None, None

def fetch_usgs_quakes(min_magnitude=4.5, days=90, lat=None, lon=None, radius_km=None):
    start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {
        "format": "geojson",
        "starttime": start_date,
        "minmagnitude": min_magnitude,
        "limit": 2000
    }
    # Ensure lat, lon, and radius are passed for location-based filtering
    if lat and lon and radius_km:
        print(f"Fetching data within {radius_km} km of {lat}, {lon}")
        params.update({
            "latitude": lat,
            "longitude": lon,
            "maxradiuskm": radius_km
        })

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    res = requests.get(url, params=params)
    res.raise_for_status()
    features = res.json()["features"]

    quakes = []
    for f in features:
        mag = f["properties"]["mag"]
        place = f["properties"]["place"]
        timestamp = f["properties"]["time"] / 1000
        time = datetime.utcfromtimestamp(timestamp)
        quakes.append([time.isoformat(), mag, place])

    return quakes

# Estimate Recurrence Interval and Probability
def estimate_recurrence_interval(quake_data, minmag):
    # Extract timestamps of the earthquakes
    timestamps = [q[0] for q in quake_data]
    magnitudes = [q[1] for q in quake_data]

    # Filter major quakes (>= minmag)
    major_quakes = [q for q in zip(timestamps, magnitudes) if q[1] >= minmag]

    # Convert timestamps to datetime objects
    dates = [datetime.fromisoformat(ts) for ts, _ in major_quakes]

    # Group quakes by year
    years = [d.year for d in dates]
    years.sort()

    # Calculate gaps between years (gaps = difference between consecutive years with quakes)
    major_years = sorted(set(years))
    gaps = [major_years[i+1] - major_years[i] for i in range(len(major_years) - 1)]

    # Handle case if no gaps are available (e.g., too few quakes)
    if len(gaps) == 0:
        print(Fore.RED + "Not enough data to calculate recurrence intervals.")
        return

    # Calculate mean gap (mean recurrence interval)
    mean_gap = np.mean(gaps)
    probability = 1 / mean_gap if mean_gap > 0 else 0

    # Cap the probability to avoid unrealistic values
    if probability > 1:
        probability = 1

    # Print results
    print(Fore.GREEN + f"Mean Recurrence Interval (based on years): {mean_gap:.2f} years")
    print(Fore.YELLOW + f"Estimated Probability of a major earthquake occurring in 1 year: {probability:.4f}")

    # Add a text-based message for the probability estimate
    if probability >= 0.75:
        print(Fore.GREEN + f"The estimated probability of a major earthquake (≥ {minmag} magnitude) is HIGH. There is a significant likelihood of occurrence within the next year.")
    else:
        print(Fore.RED + f"The estimated probability of a major earthquake (≥ {minmag} magnitude) is LOW. The likelihood of occurrence within the next year is minimal.")

def main():
    parser = argparse.ArgumentParser(description="Analyze quake recurrence intervals.")
    parser.add_argument("--data", help="List of quakes as [[timestamp, magnitude, 'location'], ...]")
    parser.add_argument("--fetch", action="store_true", help="Fetch recent quakes from USGS")
    parser.add_argument("--minmag", type=float, default=6.0, help="Min magnitude to filter quakes")
    parser.add_argument("--days", type=int, default=365*5, help="Days back to fetch data (only with --fetch)")
    parser.add_argument("--location", type=str, help="Location name to filter (city/state/country)")
    parser.add_argument("--radius", type=float, help="Radius in km for regional filter")
    parser.add_argument("--export", action="store_true", help="Export filtered quakes to CSV")
    parser.add_argument("--plot", action="store_true", help="Plot quakes per year chart")
    parser.add_argument("--estimate", action="store_true", help="Estimate the recurrence interval and probability of major quakes")
    args = parser.parse_args()

    # Fetch or load quake data
    if args.estimate:
        print(Fore.CYAN + "Performing Recurrence Interval and Probability Estimation...")
        if args.data:
            try:
                quake_data = ast.literal_eval(args.data)
            except Exception as e:
                print(Fore.RED + "Invalid data format. Make sure it's a Python-style list.")
                return
            estimate_recurrence_interval(quake_data, args.minmag)  # Pass minmag here
        elif args.fetch:
            lat, lon = None, None
            if args.location:
                lat, lon = get_location_coords(args.location)  # Get coordinates for location
            quake_data = fetch_usgs_quakes(
                min_magnitude=args.minmag,
                days=args.days,
                lat=lat,
                lon=lon,
                radius_km=args.radius  # Apply radius filter if provided
            )
            estimate_recurrence_interval(quake_data, args.minmag)  # Pass minmag here
        else:
            print(Fore.RED + "Provide --data or --fetch for earthquake data.")
            return
        return

    if args.fetch:
        lat, lon = None, None
        if args.location:
            lat, lon = get_location_coords(args.location)  # Get coordinates for location
        quake_data = fetch_usgs_quakes(
            min_magnitude=args.minmag,
            days=args.days,
            lat=lat,
            lon=lon,
            radius_km=args.radius  # Apply radius filter if provided
        )
        print(Fore.WHITE + f"Fetched {len(quake_data)} quakes")
    elif args.data:
        try:
            quake_data = ast.literal_eval(args.data)
        except Exception as e:
            print(Fore.RED + "Invalid data format. Make sure it's a Python-style list.")
            return
    else:
        print(Fore.RED + "Provide --data or --fetch")
        return

    # Process quake list
    quakes = []
    for q in quake_data:
        event_time = datetime.fromisoformat(q[0])
        event_year = event_time.year
        magnitude = float(q[1])
        location = q[2] if len(q) > 2 else "Unknown"
        years_ago = round((datetime.now() - event_time).days / 365.25, 2)

        quakes.append({
            "Years Ago": years_ago,
            "Magnitude": magnitude,
            "Date": event_year,
            "Timestamp": event_time.isoformat(),
            "Location": location,
            "Type": f"Major (≥ {args.minmag})" if magnitude >= args.minmag else f"Moderate (< {args.minmag})"
        })

    df = pd.DataFrame(quakes)
    if df.empty:
        print(Fore.RED + "No earthquake data found after filtering. Exiting.")
        return
    df.sort_values(by="Date", ascending=False, inplace=True)

    df_major = df[df["Magnitude"] >= args.minmag].copy()
    df_major["Date"] = df_major["Date"].astype(int)
    major_years = sorted(set(df_major["Date"].tolist()))
    gaps = [major_years[i+1] - major_years[i] for i in range(len(major_years) - 1)]
    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    # Display major earthquake analysis with estimate
    print(Fore.GREEN + "\n=== MAJOR EARTHQUAKE ANALYSIS ===")
    print(Fore.YELLOW + f"Total major quakes (≥ {args.minmag}):", len(df_major))
    print(Fore.CYAN + "Years:", major_years)
    print(Fore.CYAN + "Gaps between events:", gaps)
    print(Fore.CYAN + "Average recurrence interval:", round(avg_gap, 2), "years")
    estimate_recurrence_interval(quake_data, args.minmag) 

    per_year = df_major.groupby("Date").size()
    print(Fore.GREEN + "\n=== QUAKES PER YEAR ===")
    print(Fore.WHITE + per_year.to_string())

    if args.export:
        export_time = datetime.utcnow()
        export_iso = export_time.isoformat()
        export_filename = f"major_quakes_{export_time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        df_major["QuakeAnalyzer_Timestamp"] = export_iso
        df_major.to_csv(export_filename, index=False)
        print(Fore.MAGENTA + f"Exported {len(df_major)} major quakes to '{export_filename}' at {export_iso}")

    if args.plot:
        try:
            import matplotlib.pyplot as plt
            per_year.plot(kind='bar', figsize=(12, 4), title=f'Quakes ≥ {args.minmag} Per Year')
            plt.ylabel(f'Count (≥ {args.minmag})')
            plt.xlabel('Year')
            plt.tight_layout()
            plt.show()

        except ImportError:
            print(Fore.RED + "matplotlib not installed. Run: pip install matplotlib")

if __name__ == "__main__":
    main()
