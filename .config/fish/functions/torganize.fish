# Defined interactively
function torganize
    rsync -auh --remove-sent-files ~/Downloads/\[(seq 0 9)*.torrent backup:.local/data/rtorrent/watch/new/
    rsync -auh --remove-sent-files ~/Downloads/*jptv.club*.torrent backup:.local/data/jptv.club/

    rsync -auh --remove-sent-files ~/Downloads/\[OldToons*.torrent backup:.local/data/qbittorrent/seed/oldtoons_world/

    rsync -auh --remove-sent-files ~/Downloads/\[HappyFappy\]*.torrent backup:.local/data/qbittorrent/porn/happyfappy/
    rsync -auh --remove-sent-files ~/Downloads/\[pornolab.net\]*.torrent backup:.local/data/qbittorrent/porn/pornolab.net/

    rsync -auh --remove-sent-files ~/Downloads/*.torrent backup:.local/data/qbittorrent/seed/
end
