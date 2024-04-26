# Defined via `source`
function dorganize
    ~/d/sync/world/downloads/

    fd -eZIP -eRAR -e7z -x bash -c 'unar "{}" && rm "{}"'

    fd -d1 -eEPUB -edjvu -x mv "{}" ~/d/dump/text/ebooks/
    fd -d1 -eHTML -ePDF -x mv "{}" ~/d/dump/text/web/

    fd -d1 -eJPEG -x mv "{}" {.}.jpg
    fd -d1 -eJPG -ePNG -eWEBP -x mv "{}" ~/d/dump/porn/image/

    lb relmv --ext mid . ~/d/dump/audio/midi/

    remove_empty_directories
    ls
end
