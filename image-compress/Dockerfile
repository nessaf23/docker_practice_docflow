FROM python:3.11.9-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    COMPRESS_RATIO=10 \
    IMAGE_PATH=/data/images

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin appuser && \
    mkdir -p /data/images && chown 10001:10001 /data/images
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .


ENV COMPRESS_RATIO=10
USER 10001:10001
EXPOSE 18080

CMD ["python", "/app/server.py"]
