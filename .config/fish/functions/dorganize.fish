# Defined via `source`
function dorganize
    ~/sync/world/downloads/

    set rtorrent_files
    for torrent in (fd --no-ignore --max-depth=1 -e torrent ~/Downloads/)
        if string match -rq '\[[0-9].*\.torrent$' -- $torrent; and strings $torrent | rg -q 't.myan'
            set --append rtorrent_files $torrent
        end
    end
    if test (count $rtorrent_files) -gt 0
        lb mv $rtorrent_files ~/.local/data/rtorrent/watch/new/
    end
    lb mv -etorrent . ~/.local/data/qbittorrent/queue/

    lb unar -y *Subtitle*

    unardel *.zip
    unardel *.rar
    unardel *.7z
    unardel *.xz

    fd -d1 --no-ignore -eEPUB -edjvu -x mv "{}" (d dump/text/ebooks/)
    fd -d1 --no-ignore -eHTML -ePDF -x mv "{}" (d dump/text/web/)

    fd -d1 --no-ignore -eJPEG -x mv "{}" {.}.jpg
    fd -d1 --no-ignore -eJPG -ePNG -eWEBP -eGIF -eAVIF -x mv "{}" (d dump/image/)

    lb relmv --ext mid . (d dump/audio/midi/)
    lb relmv --ext srt,ass,ssa,vtt,sub,idx . (d dump/video/)
    fd --no-ignore -ersrc -enfo -x rm
    lb relmv --ext mp3,wav,mka . (d dump/audio/)

    folders.empty.delete
    ls
end
