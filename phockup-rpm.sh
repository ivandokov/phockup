#!/usr/bin/env bash

export LANGUAGE=C
export LC_ALL=C
export LANG=C

export PERL5LIB="${PERL5LIB}:/usr/local/lib/x86_64-linux-gnu/perl/5.22.1:/usr/local/share/perl/5.22.1:/usr/lib/x86_64-linux-gnu/perl5/5.22:/usr/share/perl5:/usr/lib/x86_64-linux-gnu/perl/5.22:/usr/share/perl/5.22:/usr/local/lib/site_perl:/usr/lib/x86_64-linux-gnu/perl-base"

exec "/usr/bin/python3" "/usr/lib/phockup/phockup.py" "$@"
