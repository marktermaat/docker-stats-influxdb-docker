import os
import logging
import time
import docker
import multiprocessing as mp
from datetime import datetime
from influxdb import InfluxDBClient

# Main method and loop
def main():
  init_logger()
  logging.info('Docker stats logging started')

  docker_client = client_docker_client()
  influxdb_client = open_influxdb_client()

  while True:
    timestamp = datetime.utcnow().isoformat()
    container_stats = get_all_container_stats(docker_client)
    data = convert_stats_to_data(container_stats, timestamp)
    send_data_to_influxdb(influxdb_client, data)
    time.sleep(60) # Todo: 60 seconds and configurable

# Initializes the logger
def init_logger():
  log_level_str = os.environ.get('LOG_LEVEL') or 'WARNING'
  log_level = getattr(logging, log_level_str)
  logging.basicConfig(filename='/var/log/docker_stats.log', level=log_level)

# Creates a docker client
def client_docker_client():
  client = docker.from_env()
  return client

# Opens the InfluxDB Client
def open_influxdb_client():
  host = os.environ.get('INFLUXDB_HOST') or 'localhost'
  port = int(os.environ.get('INFLUXDB_PORT') or '8086')
  user = os.environ.get('INFLUXDB_USER') or ''
  password = os.environ.get('INFLUXDB_PASSWORD') or ''
  database = os.environ.get('INFLUXDB_DATABASE')

  if database == None:
    logging.critical('No database set, use environment variable INFLUXDB_DATABASE to set it.')
    sys.exit('No database set, use environment variable INFLUXDB_DATABASE to set it.')

  try:
    client = InfluxDBClient('192.168.2.4', 8086, '', '', 'docker_stats')
    return client
  except err:
    logging.critical(f'Cannot open InfluxDB Client: {err}')
    sys.exit(f'Cannot open InfluxDB Client: {err}')

def get_all_container_stats(docker_client):
  data_queue = mp.Queue()
  processes =[ mp.Process(target=get_container_stats, args=(data_queue, container)) for container in docker_client.containers.list()]
  
  # Run processes
  for p in processes:
    p.start()

  # Exit the completed processes
  for p in processes:
    p.join()

  data = []
  while data_queue.qsize() != 0:
    data.append(data_queue.get())
  return data

# Rertrieves the container stats given the container, and puts them into the given data queue
def get_container_stats(data_queue, container):
  stats = container.stats(stream=False, decode=True)
  data = {
    "name": stats['name'],
    "mem_current": str_to_int(stats.get('memory_stats', {}).get('usage')),
    "cpu_counter": str_to_int(stats.get('cpu_stats', {}).get('cpu_usage', {}).get('total_usage')),
    "network_bytes_send": str_to_int(stats.get('networks', {}).get('eth0', {}).get('tx_bytes')),
    "network_bytes_received": str_to_int(stats.get('networks', {}).get('eth0', {}).get('rx_bytes'))
  }
  data_queue.put(data)

# Converts string to int, but returns None if input string is None too.
def str_to_int(str):
  return None if str == None else int(str)

# Converts all container stats into a data array for InfluxDB.
def convert_stats_to_data(container_stats, timestamp):
  data = []
  for stats in container_stats:
    stat_data = {
      "measurement": "docker_stats",
      "tags": {
        "container": stats['name']
      },
      "time": timestamp,
      "fields": {
        "mem_current": stats['mem_current'],
        "cpu_counter": stats['cpu_counter'],
        "network_bytes_send": stats['network_bytes_send'],
        "network_bytes_received": stats['network_bytes_received']
      }
    }
    data.append(stat_data)
  return data

# Sends the data to InfluxDB
def send_data_to_influxdb(client, data):
  client.write_points(data)
  logging.info('Data send to InfluxDB')

main()