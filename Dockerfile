# ---- Stage 1: build wheels for dependencies ----
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ---- Stage 2: the lean runtime image ----
FROM python:3.11-slim

RUN useradd --create-home --uid 1001 appuser

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .

RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && rm -rf /wheels

COPY app.py .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/health').status==200 else sys.exit(1)"

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]