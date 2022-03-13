#!/usr/bin/env bash

if [ -f /tmp/phockup.lockfile ]; then
  rm /tmp/phockup.lockfile
fi

CRON_COMMAND="$CRON flock -n /tmp/phockup.lockfile phockup /mnt/input /mnt/output $OPTIONS"
echo "$CRON_COMMAND" >> /etc/crontabs/root
echo "cron job has been set up with command: $CRON_COMMAND"

crond -f -d 8
