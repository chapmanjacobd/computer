#!/bin/bash 
set -e 
set -u 
set -o pipefail

start=$SECONDS

exts=$(ls -dp *.*| grep -v / | sed 's/^.*\.//' | sort -u) # not folders
ignore=""

while getopts ':f::i:h' flag; do
  case "$flag" in
    h)
        echo "This script sorts files from the current dir into folders of the same file type. Specific file types can be specified using -f."
        echo "flags:"
        echo '-f (string file types to sort e.g. -f "pdf csv mp3")'
        echo '-i (string file types to ignore e.g. -i "pdf")'
        exit 1
        ;;
    f)
        exts=$OPTARG;;
    i)
        ignore=$OPTARG;;
    :) 
        echo "Missing option argument for -$OPTARG" >&2; 
        exit 1;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
  esac
done

for ext in $exts 
do  
    if [[ " ${ignore} " == *" ${ext} "* ]]; then
        echo "Skiping ${ext}"
        continue
    fi
    echo Processing "$ext"
    mkdir -p "$ext"
    mv -vn *."$ext" "$ext"/
done

duration=$(( SECONDS - start ))
echo "--- Completed in $duration seconds ---"
