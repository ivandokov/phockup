#!/usr/bin/env bash

# If the CRON variable is empty, phockup gets executed once as command line tool
if [ -z "$CRON" ]; then
  phockup "$@"

# When CRON is not empty, phockup will run in a cron job until the container is stopped.
else
  if [ -f /tmp/phockup.lockfile ]; then
    rm /tmp/phockup.lockfile
  fi

  CRON_COMMAND="$CRON flock -n /tmp/phockup.lockfile phockup /mnt/input /mnt/output $OPTIONS"

  echo "$CRON_COMMAND" >> /etc/crontabs/root
  echo "cron job has been set up with command: $CRON_COMMAND"

  crond -f -d 8
fi
