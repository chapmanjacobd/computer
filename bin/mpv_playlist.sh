#!/bin/sh

exec >/dev/null 2>&1

if [ -e /tmp/mpv.socket ] && pgrep mpv; then
    echo loadfile "$1" append | socat - /tmp/mpv.socket
else
    setsid -f mpv --no-terminal --input-ipc-server=/tmp/mpv.socket "$1"
fi
