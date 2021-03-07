#!/bin/sh

CURRENT_DIR=$( dirname $0 )

logfile="$CURRENT_DIR/howdy_source_selected.txt"

touch "$logfile"
chmod 664 "$logfile"
echo $(date +"%Y-%m-%d_%H-%M-%S") | tee "$logfile"
echo `v4l2-ctl --list-devices` >> "$logfile"
/usr/bin/sudo "$CURRENT_DIR/select_howdy_source.py" >> "$logfile" 2>&1
