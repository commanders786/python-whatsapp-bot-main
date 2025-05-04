# Build stage
FROM python:3.10-slim AS builder
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt -f https://download.pytorch.org/whl/cpu/torch_stable.html && \
    find /root/.local \
        \( -type d -name test -o -name tests -o -name __pycache__ \) -prune -exec rm -rf '{}' + && \
    find /root/.local \
        \( -type f -name '*.pyc' -o -name '*.pyo' -o -name '*.dist-info' -o -name '*.egg-info' \) -exec rm -rf '{}' +
# Final stage
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
COPY run.py .
COPY result.json .  # or result.json.gz
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "run.py"]