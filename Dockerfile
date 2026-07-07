# Optional: bakes in Playwright + browser binaries for the full tiered fetch
# (static -> headless). Not required to run/evaluate the core deliverable --
# see ADR-005 for the reproducibility rationale.
FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt playwright

COPY . .

ENTRYPOINT ["python", "main.py"]
