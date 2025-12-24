FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    gfortran \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

COPY lightfm_requirements_ubuntu.txt .
RUN pip install --no-cache-dir -r lightfm_requirements_ubuntu.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "fastapi_place:app", "--host", "0.0.0.0", "--port", "8002"]

