FROM python

WORKDIR /app

COPY requirements.txt server.py .
RUN pip install --no-cache-dir -r requirements.txt

CMD python /app/server.py
