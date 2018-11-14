# docker-stats-influxdb-docker
A script to read docker stats and send it to InfluxDB

# Description
This script calls `docker stats` on all containers running on the host, plucks out a few values and sends these to InfluxDB.

# How to use
The script is packaged as a Docker container, so it needs Docker to run. You can either use Docker directly:

`docker run -it --rm -e INFLUXDB_DATABASE='my-data' -v ./log:/var/log -v /var/run/docker.sock:/var/run/docker.sock marktermaat/docker-stats-influxdb:latest python`

Or use the example docker-compose file and run:

`docker-compose up -d`

Keep in mind that log files are put (inside the Docker container) in /var/log, so if you want to see those log files you should bind that directory to one on the host machine.

# Configuration
The following environment variables can be set.

| Variable name     | Description                                                            | Default   | Required? |
| ----------------- | ---------------------------------------------------------------------- | --------- | --------- |
| LOG_LEVEL         | The log level to use. Can be CRITICAL, ERROR, WARNING, INFO, OR DEBUG. | WARNING   |           |
| INFLUXDB_HOST     | The hostname of the InfluxDB server                                    | localhost |           |
| INFLUXDB_PORT     | The port of the InfluxDB server                                        | 8086      |           |
| INFLUXDB_USER     | The username to connect to the InfluxDB server                         |           |           |
| INFLUXDB_PASSWORD | The password to connect to the InfluxDB server                         |           |           |
| INFLUXDB_DATABASE | The database name InfluxDB to send the data to                         |           | Required  |

# Development

- `docker build --tag marktermaat/docker-stats-influxdb .`
- `docker push marktermaat/docker-stats-influxdb`

# ToDo:

- More configurable (docker.sock location? Configurable which metrics to send?)
- More metrics:
  -   CPU percentage (see https://github.com/21stio/collectd-docker-stats-plugin/blob/2c3ae8b8f7186fe4e53f3f628926d46fc59f86e8/lib/Docker/DockerFormatter.py, calculate_cpu_percentage)