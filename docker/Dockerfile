FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1



WORKDIR /app

COPY ../pyproject.toml service_account.json uv.lock* ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir uv && \
    uv pip install --system .

COPY ../app ./app
#COPY torch-2.3.1+cpu-cp312-cp312-linux_x86_64.whl /tmp/torch-2.3.1+cpu-cp312-cp312-linux_x86_64.whl
#RUN pip install /tmp/torch-2.3.1+cpu-cp312-cp312-linux_x86_64.whl

EXPOSE 8000


