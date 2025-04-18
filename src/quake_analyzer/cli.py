import pandas as pd
from datetime import datetime, timedelta
import argparse
import ast
import requests
from colorama import Fore, init
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")

def load_places():
    def prep(filepath, name_col, source_name):
        print(Fore.BLUE + f"Loading {source_name}...")
        df = pd.read_csv(filepath)

        required = {name_col, "latitude", "longitude"}
        if not required.issubset(df.columns):
            print(Fore.YELLOW + f"Skipping {source_name}: missing columns {required - set(df.columns)}")
            return pd.DataFrame(columns=["name_lower", "latitude", "longitude"])

        df = df[[name_col, "latitude", "longitude"]].dropna()
        df["name_lower"] = df[name_col].str.strip().str.lower()
        return df

    cities = prep(os.path.join(DATA_DIR, "cities.csv"), "name", "cities.csv")
    countries = prep(os.path.join(DATA_DIR, "countries.csv"), "name", "countries.csv")
    states = prep(os.path.join(DATA_DIR, "states.csv"), "name", "states.csv")

    return pd.concat([cities, states, countries], ignore_index=True)

PLACE_COORDS = load_places()

init(autoreset=True)

def fetch_usgs_quakes(min_magnitude=4.5, days=90, lat=None, lon=None, radius_km=None):
    start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {
        "format": "geojson",
        "starttime": start_date,
        "minmagnitude": min_magnitude,
        "limit": 2000
    }
    if lat and lon and radius_km:
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
    args = parser.parse_args()

    if args.location:
        place = args.location.strip().lower()
        match = PLACE_COORDS[PLACE_COORDS["name_lower"] == place]
        if not match.empty:
            lat = match.iloc[0]["latitude"]
            lon = match.iloc[0]["longitude"]
            print(Fore.WHITE + f"Using coordinates for {args.location.title()}: Latitude {lat}, Longitude {lon}")
        else:
            print(Fore.RED + f"Coordinates for '{args.location}' not found in available datasets.")
            return
    else:
        lat = lon = None

    if args.fetch:
        quake_data = fetch_usgs_quakes(
            min_magnitude=args.minmag,
            days=args.days,
            lat=lat,
            lon=lon,
            radius_km=args.radius
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

    print(Fore.GREEN + "\n=== MAJOR EARTHQUAKE ANALYSIS ===")
    print(Fore.YELLOW + f"Total major quakes (≥ {args.minmag}):", len(df_major))
    print(Fore.CYAN + "Years:", major_years)
    print(Fore.CYAN + "Gaps between events:", gaps)
    print(Fore.CYAN + "Average recurrence interval:", round(avg_gap, 2), "years")

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