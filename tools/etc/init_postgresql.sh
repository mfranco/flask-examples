#!/bin/sh
/usr/bin/pg_ctl  restart
sleep 4
tail -f /dev/null
