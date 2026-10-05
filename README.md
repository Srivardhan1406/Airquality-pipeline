# Air Quality Monitoring Data Pipeline
**Linux + Git + Docker + REST API data engineering fundamentals**

Collects live air-quality (PM2.5, PM10, CO, NO2, ozone, AQI) and weather data for 5 Indian cities
from the free [Open-Meteo](https://open-meteo.com) REST APIs (no API key), lands it in a secure
data landing zone, logs every call, and analyses the logs with Linux commands.

## Project structure
```
airquality-pipeline/
├── scripts/
│   ├── setup_landing_zone.sh     # secure folders + permissions (chmod/umask)
│   ├── analyze_logs.sh           # log analysis with grep/awk/cut/sort/uniq/wc
│   └── git_workflow_demo.sh      # branches, commits, merges, PR instructions
├── src/
│   ├── collect_data.py           # REST API ingestion + retries + logging
│   └── generate_sample_logs.py   # creates a 1,440-line sample log
├── sample_logs/pipeline_sample.log
├── Dockerfile  docker-compose.yml  requirements.txt  .gitignore
└── docs/
```

## Run in VS Code
Open the folder in VS Code, then open a terminal (**Git Bash** or **WSL** on Windows; the default terminal on Mac/Linux).

```bash
# 1. Secure landing zone
bash scripts/setup_landing_zone.sh

# 2. Python environment
python -m venv .venv
source .venv/bin/activate          # Git Bash on Windows: source .venv/Scripts/activate
pip install -r requirements.txt

# 3. Collect data from REST APIs (add --offline if no internet)
python src/collect_data.py

# 4. Analyse logs with Linux commands
bash scripts/analyze_logs.sh                    # sample log
bash scripts/analyze_logs.sh logs/pipeline.log  # your real run

# 5. Docker
docker compose up --build
docker compose run --rm collector python src/collect_data.py --offline

# 6. Git branching + pull request
bash scripts/git_workflow_demo.sh
```

## Security features
- `umask 027`, directories `750`, quarantine `700`, data files `640`
- Container runs as a **non-root** user
- `data_lake/`, `logs/`, `.env` excluded from Git
- Author: Srivardhan
