FROM python:3.6-alpine
RUN pip install docker influxdb

COPY src/ /app
WORKDIR /app

CMD [ "python", "/app/docker_stats.py" ]