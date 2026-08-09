# Publisher image: a tiny paho-mqtt client that generates deterministic MQTT
# test traffic against the broker.
#
# Build context is the mqtt/ directory (see docker-compose.yml).
FROM python:3.12-slim

WORKDIR /app

# Install the MQTT client library first (better layer caching).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# The publisher script.
COPY publisher.py ./

# Unbuffered stdout so `docker compose logs publisher` streams in real time.
ENV PYTHONUNBUFFERED=1

CMD ["python", "publisher.py"]
