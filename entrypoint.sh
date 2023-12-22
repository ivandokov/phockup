#!/usr/bin/env bash

if [[ "$PHOCKUP_UID" != "" && "$PHOCKUP_GID" != "" ]]
then
	adduser -D -u $PHOCKUP_UID $PHOCKUP_UID || echo "User $PHOCKUP_UID already exists"
	addgroup -g $PHOCKUP_GID $PHOCKUP_GID || echo "Group $PHOCKUP_GID already exists"
	GNAME=`getent group $PHOCKUP_GID | cut -d: -f1`
	if [ -z "$CRON" ]; then
		su $PHOCKUP_UID -g $GNAME -c "phockup $*"
	else
		if [ -f /tmp/phockup.lockfile ]; then
			rm /tmp/phockup.lockfile
		fi

		CRON_COMMAND="$CRON flock -n /tmp/phockup.lockfile su $PHOCKUP_UID -g $GNAME -c \"phockup /mnt/input /mnt/output $OPTIONS\""

		echo "$CRON_COMMAND" >> /etc/crontabs/root
		echo "cron job has been set up with command: $CRON_COMMAND"

		crond -f -d 8
	fi
else
	if [ -z "$CRON" ]; then
		phockup "$@"
	else
		if [ -f /tmp/phockup.lockfile ]; then
			rm /tmp/phockup.lockfile
		fi

		CRON_COMMAND="$CRON flock -n /tmp/phockup.lockfile phockup /mnt/input /mnt/output $OPTIONS"

		echo "$CRON_COMMAND" >> /etc/crontabs/root
		echo "cron job has been set up with command: $CRON_COMMAND"

		crond -f -d 8
	fi
fi

