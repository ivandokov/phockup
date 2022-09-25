#!/usr/bin/env bash

chown -R $PUID:$PGID /mnt/input
chown -R $PUID:$PGID /mnt/output

# If the CRON variable is empty, phockup gets executed once as command line tool
if [ -z "$CRON" ]; then
  /phockup.py $@

# When CRON is not empty, phockup will run in a cron job until the container is stopped.
else
  if [ -f /tmp/phockup.lockfile ]; then
    rm /tmp/phockup.lockfile
  fi

  CRON_COMMAND="$CRON flock -n /tmp/phockup.lockfile /phockup.py /mnt/input /mnt/output $OPTIONS"

  crontab -l > mycron
  echo "$CRON_COMMAND" >> mycron
  crontab mycron
  rm mycron

  echo "cron job has been set up with command: $CRON_COMMAND"

  crond -f -d 8
fi
