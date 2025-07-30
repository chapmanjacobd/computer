#!/bin/bash

case "$1" in
    /net/*)
        /bin/setsid -f rm "$1"
        ;;

    *)
        /bin/setsid -f trash "$1"
        ;;
esac
