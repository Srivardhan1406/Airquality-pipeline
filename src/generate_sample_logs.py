"""Generate a realistic pipeline log (500+ lines) so log analysis can be demonstrated."""
import os, random
from datetime import datetime, timedelta
random.seed(7)
cities = ["Hyderabad", "Mumbai", "Delhi", "Bengaluru", "Chennai"]
t = datetime(2026, 10, 1, 0, 0, 0)
lines = []
for i in range(120):
    t += timedelta(minutes=random.randint(20, 40))
    lines.append(f"{t:%Y-%m-%d %H:%M:%S} | INFO | run_started | cities=5 | offline=False")
    for c in cities:
        for api in ("air-quality-api", "api"):
            t += timedelta(seconds=random.randint(1, 3))
            r = random.random()
            ms = random.randint(120, 900)
            if r < 0.06:
                lines.append(f"{t:%Y-%m-%d %H:%M:%S} | WARNING | city={c} | api_call_failed | attempt=1 | error=Timeout")
            elif r < 0.08:
                lines.append(f"{t:%Y-%m-%d %H:%M:%S} | ERROR | city={c} | api_call_failed | attempt=3 | error=ConnectionError")
            elif r < 0.10:
                lines.append(f"{t:%Y-%m-%d %H:%M:%S} | INFO | city={c} | api={api} | status=429 | latency_ms={ms} | attempt=1")
            else:
                lines.append(f"{t:%Y-%m-%d %H:%M:%S} | INFO | city={c} | api={api} | status=200 | latency_ms={ms} | attempt=1")
    lines.append(f"{t:%Y-%m-%d %H:%M:%S} | INFO | run_finished | records={random.choice([4,5,5,5])} | failed=0")
os.makedirs("sample_logs", exist_ok=True)
open("sample_logs/pipeline_sample.log", "w").write("\n".join(lines) + "\n")
print(f"Wrote {len(lines)} lines to sample_logs/pipeline_sample.log")
