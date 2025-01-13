# Defined via `source`
function dorganize
    ~/sync/world/downloads/

    unardel *.zip
    unardel *.rar
    unardel *.7z
    unardel *.xz

    fd -d1 -eEPUB -edjvu -x mv "{}" ~/d/dump/text/ebooks/
    fd -d1 -eHTML -ePDF -x mv "{}" ~/d/dump/text/web/

    fd -d1 -eJPEG -x mv "{}" {.}.jpg
    fd -d1 -eJPG -ePNG -eWEBP -eGIF -eAVIF -x mv "{}" ~/d/dump/image/

    lb relmv --ext mid . ~/d/dump/audio/midi/
    lb relmv --ext srt,ass,vtt,sub,idx . ~/d/dump/video/
    lb relmv --ext mp3,wav . ~/d/dump/audio/

    remove_empty_directories
    ls
end
