
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \

PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \

curl ca-certificates \

&& rm -rf /var/lib/apt/lists/*

COPY . /app

RUN python -m pip install -U pip setuptools wheel \

&& if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi \

&& pip install --no-cache-dir "psycopg[binary]" fastapi "uvicorn[standard]"

EXPOSE 8000

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]

