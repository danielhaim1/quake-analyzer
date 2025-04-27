import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
import argparse
import ast
import requests
from colorama import Fore, init, Back, Style
from importlib.resources import files

# ────────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ────────────────────────────────────────────────────────────────────────────────

def get_data_path(filename: str):
    """Return absolute path to a data file bundled with the package."""
    return files("quake_analyzer").joinpath("data", filename)


def load_places() -> pd.DataFrame:
    """Load gazetteer tables (cities, states, countries) into one DataFrame."""

    def prep(filepath: str, name_col: str, tag: str) -> pd.DataFrame:
        print(Fore.LIGHTBLACK_EX + f"Loading {tag}…")
        df = pd.read_csv(filepath)
        required = {name_col, "latitude", "longitude"}
        if not required.issubset(df.columns):
            print(
                Fore.LIGHTBLACK_EX
                + f"Skipping {tag}: missing {required - set(df.columns)}"
            )
            return pd.DataFrame(columns=["name_lower", "latitude", "longitude"])
        df = df[[name_col, "latitude", "longitude"]].dropna()
        df["name_lower"] = df[name_col].str.strip().str.lower()
        return df

    cities = prep(get_data_path("cities.csv"), "name", "cities.csv")
    states = prep(get_data_path("states.csv"), "name", "states.csv")
    countries = prep(get_data_path("countries.csv"), "name", "countries.csv")
    return pd.concat([cities, states, countries], ignore_index=True)



PLACE_COORDS = load_places()
init(autoreset=True)

# ────────────────────────────────────────────────────────────────────────────────
# Geocoding helpers
# ────────────────────────────────────────────────────────────────────────────────

def get_location_coords(place: str):
    row = PLACE_COORDS[PLACE_COORDS["name_lower"] == place.strip().lower()]
    if row.empty:
        print(Fore.RED + f"Location '{place}' not found in gazetteer.")
        return None, None
    return float(row.iloc[0]["latitude"]), float(row.iloc[0]["longitude"])


# ────────────────────────────────────────────────────────────────────────────────
# USGS fetcher
# ────────────────────────────────────────────────────────────────────────────────

def fetch_usgs_quakes(
    *,
    min_magnitude: float = 4.5,
    days: int = 90,
    start: str | None = None,
    end: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    radius_km: float | None = None,
):
    now = datetime.utcnow()
    start_date = start if start else (now - timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = end if end else (now + timedelta(days=1)).strftime("%Y-%m-%d")

    print(Fore.WHITE + f"[DEBUG] USGS fetch range: {start_date} → {end_date}")

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params: dict[str, str | float] = {
        "format": "geojson",
        "starttime": start_date,
        "endtime": end_date,
        "minmagnitude": min_magnitude,
        "limit": 2000,
        "orderby": "time",
    }
    if lat and lon and radius_km:
        print(f"Fetching data within {radius_km} km of {lat}, {lon}")
        params.update({"latitude": lat, "longitude": lon, "maxradiuskm": radius_km})

    # print(Fore.WHITE + "[DEBUG] Final request URL:")
    # print(Fore.CYAN + requests.Request('GET', url, params=params).prepare().url)

    res = requests.get(url, params=params, timeout=60)
    res.raise_for_status()
    quakes: list[list[str | float]] = []
    for feat in res.json()["features"]:
        prop = feat["properties"]
        ts = prop["time"] / 1000.0
        quakes.append(
            [datetime.utcfromtimestamp(ts).isoformat(timespec="seconds"), prop["mag"], prop["place"]]
        )

    if quakes:
        newest = quakes[0]
        bold, reset = "\033[1m", "\033[0m"
        bg = Back.RED
        fg = Fore.WHITE

        print()
        print(Fore.MAGENTA + "\n" + "─" * 8 + "[ LATEST DATA ]" + "─" * 8)
        print(bg + fg + f"UTC:       {newest[0]}" + reset)
        print(bg + fg + f"Magnitude: {newest[1]}" + reset)
        print(bg + fg + f"Location:  {newest[2]}" + reset)

    return quakes


# ────────────────────────────────────────────────────────────────────────────────
# Risk metrics
# ────────────────────────────────────────────────────────────────────────────────

def compute_risk_stats(quake_data: list[list], minmag: float):
    major = [
        (datetime.fromisoformat(iso), float(mag))
        for iso, mag, *_ in quake_data
        if float(mag) >= minmag
    ]
    if not major:
        return None

    major.sort(key=lambda t: t[0], reverse=True)
    years = sorted({dt.year for dt, _ in major})
    gaps = [years[i + 1] - years[i] for i in range(len(years) - 1)]
    if gaps:
        mean_gap = float(np.mean(gaps))
        lam = 1.0 / mean_gap
        prob_1 = 1.0 - math.exp(-lam)
        prob_10 = 1.0 - math.exp(-lam * 10)
    else:
        mean_gap = prob_1 = prob_10 = None

    if prob_1 is None:
        label, color = "UNKNOWN", Fore.WHITE
    elif prob_1 >= 0.75:
        label, color = "HIGH likelihood", Fore.GREEN
    elif prob_1 >= 0.25:
        label, color = "MODERATE likelihood", Fore.YELLOW
    else:
        label, color = "LOW likelihood", Fore.RED

    return {
        "newest": major[0][0],
        "years_ago": (datetime.utcnow() - major[0][0]).days / 365.25,
        "count": len(major),
        "start_date": major[-1][0].date(),
        "mean_gap": mean_gap,
        "prob_1": prob_1,
        "prob_10": prob_10,
        "risk_label": label,
        "risk_color": color,
    }


def display_risk_section(stats: dict, minmag: float):
    if not stats or stats.get("mean_gap") is None:
        print(Fore.RED + "Not enough data to estimate earthquake risk.")
        return

    bold, reset = "\033[1m", "\033[0m"
    today = datetime.utcnow().date()

    print(Fore.MAGENTA + "\n" + "─" * 8 + "[ EARTHQUAKE RISK ]" + "─" * 8)
    newest_str = stats["newest"].strftime("%Y-%m-%dT%H:%M")
    years_ago = stats["years_ago"]

    if years_ago < 1:
        age_str = f"{int((datetime.utcnow() - stats['newest']).days)} days ago"
    else:
        age_str = f"{years_ago:.1f} y ago"

    print(Fore.CYAN + f"Newest quake (UTC): {newest_str}  •  {age_str}")

    print(
        Fore.CYAN
        + (
            f"Quakes analyzed: {stats['count']} (≥ {minmag:.1f}, "
            f"{stats['start_date']} → {today})"
        )
    )

    bold, reset = "\033[1m", "\033[0m"
    bg = Back.RED
    fg = Fore.WHITE

    print()
    print(f"{bg}{fg}Mean recurrence:    {bold}{stats['mean_gap']:>6.2f} years{reset}")
    print(f"{bg}{fg}1-year probability: {bold}{stats['prob_1']*100:>6.2f}%{reset}")
    print(f"{bg}{fg}10-year probability:{bold}{stats['prob_10']*100:>6.2f}%{reset}")
    print(f"")

    print(stats["risk_color"] + bold + stats["risk_label"] + reset + " - improbable in the next year.")
    print(Fore.LIGHTBLACK_EX + "(Poisson model; real recurrence may differ.)")

# ────────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Analyze earthquake data, recurrence intervals & risk.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--data", help="Python-literal list of quakes [[iso, mag, place], …]")
    parser.add_argument("--yesterday", action="store_true", help="Set --end to yesterday (UTC)")
    parser.add_argument("--fetch", action="store_true", help="Fetch data from USGS")
    parser.add_argument("--minmag", type=float, default=6.0, help="Magnitude threshold")
    parser.add_argument("--days", type=int, default=365 * 5, help="Days back when fetching")
    parser.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, help="End date YYYY-MM-DD")
    parser.add_argument("--location", type=str, help="Place name (city/state/country)")
    parser.add_argument("--lat", type=float, help="Latitude if not using --location")
    parser.add_argument("--lon", type=float, help="Longitude if not using --location")
    parser.add_argument("--radius", type=float, help="Search radius km around lat/lon")
    parser.add_argument("--estimate", action="store_true", help="Compute risk banner")
    parser.add_argument("--export", action="store_true", help="Save major quakes CSV")
    parser.add_argument("--plot", action="store_true", help="Plot yearly histogram")
    parser.add_argument("--verbose", action="store_true", help="Verbose/debug logging")
    args = parser.parse_args()

    vprint = (lambda m: print(Fore.WHITE + "[DEBUG] " + m)) if args.verbose else (lambda *_: None)

    # adjust --end if yesterday flag

    if args.yesterday and not args.end:
        args.end = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT23:59:59")
        vprint(f"Set --end to {args.end} (UTC) due to --yesterday")


    # verbose print helper
    vprint = (lambda m: print(Fore.WHITE + "[DEBUG] " + m)) if args.verbose else (lambda *_: None)

    # ── Load or fetch quake data
    if args.data:
        try:
            quake_data = ast.literal_eval(args.data)
            vprint(f"Loaded {len(quake_data)} events from --data")
        except Exception:
            print(Fore.RED + "Invalid --data literal.")
            return
    elif args.fetch:
        lat, lon = args.lat, args.lon
        if args.location:
            lat, lon = get_location_coords(args.location)
            if lat is None or lon is None:
                print(Fore.RED + "Unknown location. Aborting.")
                return
        quake_data = fetch_usgs_quakes(
            min_magnitude=args.minmag,
            days=args.days,
            start=args.start,
            end=args.end,
            lat=lat,
            lon=lon,
            radius_km=args.radius,
        )
        vprint(f"Fetched {len(quake_data)} events from USGS")
    else:
        print(Fore.RED + "Provide --data or --fetch to load earthquake data.")
        return

    if not quake_data:
        print(Fore.RED + "No earthquake data found. Try adjusting --days or --minmag.")
        return

    # ── Estimation (risk section)
    if args.estimate:
        stats = compute_risk_stats(quake_data, args.minmag)
        display_risk_section(stats, args.minmag)

    # ── Summary of major quakes
    # Transform to DataFrame
    rows = []
    for iso, mag, *rest in quake_data:
        try:
            dt = datetime.fromisoformat(iso)
        except Exception:
            continue
        rows.append({
            "Years Ago": round((datetime.utcnow() - dt).days / 365.25, 2),
            "Magnitude": float(mag),
            "Date": dt.year,
            "Timestamp": dt.isoformat(timespec="seconds"),
            "Location": rest[0] if rest else "Unknown",
        })
    df = pd.DataFrame(rows)
    if df.empty:
        print(Fore.RED + "No valid earthquake records to summarize.")
        return

    df_major = df[df["Magnitude"] >= args.minmag].copy()
    df_major.sort_values("Date", ascending=False, inplace=True)
    years = sorted(df_major["Date"].astype(int).tolist())
    gaps = [years[i+1] - years[i] for i in range(len(years)-1)]
    avg_gap = float(np.mean(gaps)) if gaps else 0.0

    print(Fore.MAGENTA + "\n" + "─" * 8 + "[ QUAKE SUMMARY ]" + "─" * 8)
    print(Fore.YELLOW + f"Total major quakes (≥ {args.minmag}): {len(df_major)}")
    print(Fore.CYAN + f"Years: {years}")
    print(Fore.CYAN + f"Gaps between events: {gaps}")
    print(Fore.CYAN + f"Average recurrence interval: {avg_gap:.2f} years")

    # ── Export to CSV
    if args.export:
        filename = f"major_quakes_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        df_major.to_csv(filename, index=False)
        print(Fore.MAGENTA + f"Exported major quakes to {filename}")

    # ── Plot histogram
    if args.plot:
        try:
            import matplotlib.pyplot as plt
            df_major.groupby("Date").size().plot(
                kind="bar", title=f"Quakes ≥ {args.minmag} Per Year", figsize=(10,4)
            )
            plt.ylabel("Count")
            plt.xlabel("Year")
            plt.tight_layout()
            plt.show()
        except ImportError:
            print(Fore.RED + "matplotlib not installed (pip install matplotlib)")

if __name__ == "__main__":
    main()