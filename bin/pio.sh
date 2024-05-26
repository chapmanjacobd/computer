#!/bin/bash

[ "$1" == "" ] && echo "Error: Missing PID" && exit 1
IO=/proc/$1/io          # io data of PID
[ ! -e "$IO" ] && echo "Error: PID does not exist" && exit 2
I=3                     # interval in seconds
SECONDS=0               # reset timer

echo "Watching command $(cat /proc/$1/comm) with PID $1"

IFS=" " read rchar wchar syscr syscw rbytes wbytes cwbytes < <(cut -d " " -f2 $IO | tr "\n" " ")

while [ -e $IO ]; do
    IFS=" " read rchart wchart syscrt syscwt rbytest wbytest cwbytest < <(cut -d " " -f2 $IO | tr "\n" " ")

    S=$SECONDS
    [ $S -eq 0 ] && continue

cat << EOF
read_bytes:            $((($rbytest-$rbytes)/1024/1024/$S)) MB per second
syscr:                 $((($syscrt-$syscr)/$S)) syscalls per second
write_bytes:           $((($wbytest-$wbytest)/1024/1024/$S)) MB per second
syscw:                 $((($syscwt-$syscw)/$S)) syscalls per second
EOF
    echo
    sleep $I
done
