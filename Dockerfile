FROM python:3.11-slim
WORKDIR /app
RUN useradd -m pipeline
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
RUN mkdir -p data_lake/landing/raw data_lake/landing/quarantine logs && chown -R pipeline:pipeline /app
USER pipeline
CMD ["python", "src/collect_data.py"]
