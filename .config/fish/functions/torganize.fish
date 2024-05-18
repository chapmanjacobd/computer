# Defined interactively
function torganize
    rsync -auh --remove-sent-files ~/Downloads/\[(seq 0 9)*.torrent backup:.local/data/rtorrent/watch/new/
    rsync -auh --remove-sent-files ~/Downloads/*jptv.club*.torrent backup:.local/data/jptv.club/

    rsync -auh --remove-sent-files ~/Downloads/\[OldToons*.torrent backup:.local/data/qbittorrent/seed/oldtoons_world/
    rsync -auh --remove-sent-files ~/Downloads/\[CarPT*.torrent backup:.local/data/qbittorrent/seed/carpt.net/

    rsync -auh --remove-sent-files ~/Downloads/\[HappyFappy*.torrent backup:.local/data/qbittorrent/porn/happyfappy/
    rsync -auh --remove-sent-files ~/Downloads/\[pornolab*.torrent backup:.local/data/qbittorrent/porn/pornolab/
    rsync -auh --remove-sent-files ~/Downloads/\[exoticaz*.torrent backup:.local/data/qbittorrent/porn/exoticaz/

    rsync -auh --remove-sent-files ~/Downloads/*.torrent backup:.local/data/qbittorrent/seed_pause/others/
end
