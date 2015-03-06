#!/bin/sh
# Cron Job script for taking and parsing snapshots

. $HOME/.cronfile
./python/cqtakesnapshot.py
./python/parse_snapshots.py
./python/doneTasksToXML.py
./python/runningTasksToXML.py
