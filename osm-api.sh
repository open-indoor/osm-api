#!/bin/bash

set -x
set -echo

mkdir -p /data/osm
chmod +x /usr/bin/tic
chmod +x /usr/bin/action.py

export API_URL=${API_URL:-https://${API_DOMAIN_NAME}}

crontab -l | { cat; echo "* * * * * /usr/bin/tic > /dev/stdout 2> /dev/stderr"; } | crontab -

echo "Start cron task" && crontab -l && /usr/sbin/crond -l 8

cat /usr/bin/action

nohup tic 2>/dev/null 1>/dev/null &

cat /tmp/Caddyfile | envsubst | tee /etc/caddy/Caddyfile

caddy run --watch --config /etc/caddy/Caddyfile