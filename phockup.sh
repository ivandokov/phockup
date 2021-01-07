#!/usr/bin/env bash

export LANGUAGE=C
export LC_ALL=C
export LANG=C

export PERL5LIB="${PERL5LIB}:${SNAP}/usr/local/lib/x86_64-linux-gnu/perl/5.22.1:${SNAP}/usr/local/share/perl/5.22.1:${SNAP}/usr/lib/x86_64-linux-gnu/perl5/5.22:${SNAP}/usr/share/perl5:${SNAP}/usr/lib/x86_64-linux-gnu/perl/5.22:${SNAP}/usr/share/perl/5.22:${SNAP}/usr/local/lib/site_perl:${SNAP}/usr/lib/x86_64-linux-gnu/perl-base"

exec "$SNAP/usr/bin/python3" "$SNAP/phockup.py" "$@"
