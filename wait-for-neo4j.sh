#!/bin/sh

set -e
host="localhost"
cmd="$@"
celerycmd="celery -A LetsMapYourNetwork worker -l warning"
rabbitmqcmd="rabbitmq-server start"

until curl -sI http://"$host":7474 | grep "200 OK"; do
  >&2 echo "Neo4j isn't available. Let's wait for sometime"
echo $cmd
  sleep 1
done

>&2 echo "Neo4j is up now. Let's go..."
echo "Starting RabbitMQ Server..."
$rabbitmqcmd &
sleep 10
echo "Starting Celery worker..."
$celerycmd &
sleep 5
echo "Starting Lets Map Your Network console..."
exec $cmd
