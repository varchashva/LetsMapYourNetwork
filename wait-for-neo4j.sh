#!/bin/sh

set -e
host="localhost"
cmd="$@"

until curl -sI http://"$host":7474 | grep "200 OK"; do
  >&2 echo "Neo4j isn't available. Let's wait for sometime"
echo $cmd
  sleep 1
done

>&2 echo "Neo4j is up now. Let's go..."
exec $cmd