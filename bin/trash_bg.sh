#!/bin/bash

case "$1" in
    /net/* | */.Trash/* | */.Trash-1000/*)
        /bin/setsid -f rm "$1"
        ;;

    *)
        /bin/setsid -f trash "$1"
        ;;
esac
