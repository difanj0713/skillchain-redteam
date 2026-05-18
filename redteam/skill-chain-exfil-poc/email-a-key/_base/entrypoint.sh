#!/bin/bash
set -e

mkdir -p /var/exfil/inbox /var/log/redteam
chmod 777 /var/exfil /var/exfil/inbox /var/log/redteam

python3 /usr/local/bin/smtp_catcher.py > /var/log/redteam/smtp_catcher.log 2>&1 &
echo $! > /var/run/smtp_catcher.pid

for i in 1 2 3 4 5 6 7 8 9 10; do
  if (echo > /dev/tcp/127.0.0.1/1025) 2>/dev/null; then
    break
  fi
  sleep 0.5
done

exec "$@"
