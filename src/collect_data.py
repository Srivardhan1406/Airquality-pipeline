"""Collect air-quality + weather data from the free Open-Meteo REST APIs
(no API key needed) and write it to the landing zone with structured logs."""
import json, csv, os, sys, time, logging, argparse, random
from datetime import datetime, timezone

import requests

CITIES = {
    "Hyderabad": (17.3850, 78.4867),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
}
AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WX_URL = "https://api.open-meteo.com/v1/forecast"

LANDING = os.getenv("LANDING_DIR", "data_lake/landing/raw")
QUARANTINE = os.getenv("QUARANTINE_DIR", "data_lake/landing/quarantine")
LOG_FILE = os.getenv("LOG_FILE", "logs/pipeline.log")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("collector")


def call_api(url, params, city, retries=3):
    api = url.split("//")[1].split(".")[0]
    for attempt in range(1, retries + 1):
        start = time.time()
        try:
            r = requests.get(url, params=params, timeout=10)
            ms = int((time.time() - start) * 1000)
            log.info("city=%s | api=%s | status=%s | latency_ms=%d | attempt=%d",
                     city, api, r.status_code, ms, attempt)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            level = log.warning if attempt < retries else log.error
            level("city=%s | api_call_failed | attempt=%d | error=%s", city, attempt, type(e).__name__)
            time.sleep(2 ** attempt)
    return None


def offline_sample():
    """Fallback so the project still runs without internet."""
    return {"current": {"pm10": round(random.uniform(30, 150), 1), "pm2_5": round(random.uniform(15, 90), 1),
                        "carbon_monoxide": round(random.uniform(200, 900), 1),
                        "nitrogen_dioxide": round(random.uniform(5, 60), 1),
                        "ozone": round(random.uniform(20, 120), 1), "us_aqi": random.randint(40, 190),
                        "temperature_2m": round(random.uniform(22, 38), 1),
                        "relative_humidity_2m": random.randint(30, 90),
                        "wind_speed_10m": round(random.uniform(2, 20), 1)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="use generated sample data (no internet)")
    args = ap.parse_args()

    os.makedirs(LANDING, exist_ok=True)
    os.makedirs(QUARANTINE, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows, failed = [], 0
    log.info("run_started | cities=%d | offline=%s", len(CITIES), args.offline)

    for city, (lat, lon) in CITIES.items():
        if args.offline:
            aq = wx = offline_sample()
            log.info("city=%s | source=offline_sample | status=200", city)
        else:
            aq = call_api(AQ_URL, {"latitude": lat, "longitude": lon,
                          "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,us_aqi"}, city)
            wx = call_api(WX_URL, {"latitude": lat, "longitude": lon,
                          "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"}, city)
        if not aq or not wx:
            failed += 1
            log.error("city=%s | no_data_collected | skipped", city)
            continue
        a, w = aq["current"], wx["current"]
        rows.append({"city": city, "collected_at": ts, "pm2_5": a.get("pm2_5"), "pm10": a.get("pm10"),
                     "co": a.get("carbon_monoxide"), "no2": a.get("nitrogen_dioxide"), "ozone": a.get("ozone"),
                     "us_aqi": a.get("us_aqi"), "temp_c": w.get("temperature_2m"),
                     "humidity": w.get("relative_humidity_2m"), "wind_kmh": w.get("wind_speed_10m")})

    if not rows:
        log.critical("run_failed | no rows collected")
        print("No data collected. Check logs/pipeline.log"); sys.exit(1)

    json_path = os.path.join(LANDING, f"airquality_{ts}.json")
    csv_path = os.path.join(LANDING, f"airquality_{ts}.csv")
    with open(json_path, "w") as f:
        json.dump(rows, f, indent=2)
    with open(csv_path, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=rows[0].keys()); wr.writeheader(); wr.writerows(rows)
    for p in (json_path, csv_path):
        os.chmod(p, 0o640)                      # secure file permissions
    log.info("run_finished | records=%d | failed=%d | files=%s,%s", len(rows), failed, json_path, csv_path)
    print(f"Saved {len(rows)} records -> {csv_path}")


if __name__ == "__main__":
    main()
