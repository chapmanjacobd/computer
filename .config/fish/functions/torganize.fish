# Defined interactively
function torganize
    rsync -auh --remove-sent-files ~/Downloads/\[(seq 0 9)*.torrent backup:.local/data/rtorrent/watch/new/

    lb mv ~/Downloads/*.torrent ~/.local/data/qbittorrent/queue/
    lb-dev torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/

    b lb-dev computer-update computers.local.db
    b lb-dev computer-update computers.remote.db
    wait

    # lb-dev allocate-torrents computers.local.db torrents.db -v -E XXX pussytorrents.org plab.site bitporn.eu scenetime.com superbits.org exoticaz.to happyfappy.org empornium.is empornium.sx
    # lb-dev allocate-torrents computers.remote.db torrents.db -v --flex -s XXX pussytorrents.org plab.site bitporn.eu scenetime.com superbits.org exoticaz.to happyfappy.org empornium.is empornium.sx

    #torrent_promote.py --trackers -n9999 -o ~/.local/data/qbittorrent/ ~/Downloads/

    #rsync -auh --remove-sent-files ~/Downloads/*.torrent backup:.local/data/qbittorrent/seed_pause/others/
end
