FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    conda \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

CMD ["python", "-m", "src.cli.main"]
