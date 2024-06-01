# Defined interactively
function torganize
    rsync -auh --remove-sent-files ~/Downloads/\[(seq 0 9)*.torrent backup:.local/data/rtorrent/watch/new/
    rsync -auh --remove-sent-files ~/Downloads/*jptv.club*.torrent backup:.local/data/jptv.club/

    rsync -auh --remove-sent-files ~/Downloads/\[OldToons*.torrent backup:.local/data/qbittorrent/seed/oldtoons_world/
    rsync -auh --remove-sent-files ~/Downloads/\[CarPT*.torrent backup:.local/data/qbittorrent/seed/carpt.net/

    mv ~/Downloads/\[HappyFappy*.torrent ~/.local/data/qbittorrent/porn/happyfappy/
    mv ~/Downloads/\[pornolab*.torrent ~/.local/data/qbittorrent/porn/pornolab/
    mv ~/Downloads/\[exoticaz*.torrent ~/.local/data/qbittorrent/porn/exoticaz/

    rsync -auh --remove-sent-files ~/Downloads/*.torrent backup:.local/data/qbittorrent/seed_pause/others/
end
