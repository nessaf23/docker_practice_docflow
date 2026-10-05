FROM python:3.11-slim

RUN useradd -m -d /app appuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .


ENV COMPRESS_RATIO=10
USER appuser

CMD ["python", "/app/server.py"]
