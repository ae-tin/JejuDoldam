FROM python:3.11-slim

WORKDIR /app

# 🔹 lightfm 빌드에 필요한 시스템 패키지
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    gfortran \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

COPY cluster_requirements_ubuntu.txt .
RUN pip install --no-cache-dir -r cluster_requirements_ubuntu.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "fastapi_route:app", "--host", "0.0.0.0", "--port", "8001"]

