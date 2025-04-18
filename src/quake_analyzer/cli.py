import pandas as pd
from datetime import datetime, timedelta
import argparse
import ast
import requests

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
    parser.add_argument("--lat", type=float, help="Latitude for regional filter")
    parser.add_argument("--lon", type=float, help="Longitude for regional filter")
    parser.add_argument("--radius", type=float, help="Radius in km for regional filter")
    parser.add_argument("--export", action="store_true", help="Export filtered quakes to CSV")
    parser.add_argument("--plot", action="store_true", help="Plot quakes per year chart")
    args = parser.parse_args()

    if args.fetch:
        quake_data = fetch_usgs_quakes(
            min_magnitude=args.minmag,
            days=args.days,
            lat=args.lat,
            lon=args.lon,
            radius_km=args.radius
        )
        print(f"Fetched {len(quake_data)} quakes")
    elif args.data:
        try:
            quake_data = ast.literal_eval(args.data)
        except Exception as e:
            print("Invalid data format. Make sure it's a Python-style list.")
            return
    else:
        print("Provide --data or --fetch")
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
    df.sort_values(by="Date", ascending=False, inplace=True)

    # Analyze major quakes
    df_major = df[df["Magnitude"] >= args.minmag].copy()
    df_major["Date"] = df_major["Date"].astype(int)

    major_years = sorted(set(df_major["Date"].tolist()))
    gaps = [major_years[i+1] - major_years[i] for i in range(len(major_years) - 1)]
    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    print("\n=== MAJOR EARTHQUAKE ANALYSIS ===")
    print(f"Total major quakes (≥ {args.minmag}):", len(df_major))
    print("Years:", major_years)
    print("Gaps between events:", gaps)
    print("Average recurrence interval:", round(avg_gap, 2), "years")

    # Count per year
    per_year = df_major.groupby("Date").size()
    print("\n=== QUAKES PER YEAR ===")
    print(per_year)

    # Optional CSV export
    if args.export:
        export_time = datetime.utcnow()
        export_iso = export_time.isoformat()
        export_filename = f"major_quakes_{export_time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"

        df_major["QuakeAnalyzer_Timestamp"] = export_iso
        df_major.to_csv(export_filename, index=False)

        print(f"Exported {len(df_major)} major quakes to '{export_filename}' at {export_iso}")

    # Optional plot
    if args.plot:
        try:
            import matplotlib.pyplot as plt
            per_year.plot(kind='bar', figsize=(12, 4), title=f'Quakes ≥ {args.minmag} Per Year')
            plt.ylabel(f'Count (≥ {args.minmag})')
            plt.xlabel('Year')
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("matplotlib not installed. Run: pip install matplotlib")

if __name__ == "__main__":
    main()
