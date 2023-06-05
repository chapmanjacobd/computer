#!/bin/bash
if pidof -o %PPID -x “rclone-cron.sh”; then
exit 1
fi
 rclone -u sync /home/xk/drive/ gdrive:/Syncopated --log-file=/home/xk/bin/rclone.log &&
 rclone -u copy gdrive:/Syncopated /home/xk/drive/ --log-file=/home/xk/bin/rclone.log
exit
