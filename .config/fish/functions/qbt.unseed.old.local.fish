# Defined in /home/xk/.config/fish/functions/qbt.unseed.old.fish @ line 1, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function qbt.unseed.old.local
    library torrent info --complete --seeders=+4 --time-stalled=+3days --time-seeding=+80days --stop --move dump --delete-rows -v
    library torrent info --time-completed=+48h --complete --no-private --stop --move dump --delete-rows
    # check file existence, prevent ghost seed
    library torrent info --no-stopped --no-errored --ul --no-all-exists --seeders=-2 --stop --move dump --delete-rows
    # stop incomplete
    library torrent info --incomplete --time-active=+85days --time-unseeded=+100days --delete-incomplete --stop --move broken --delete-rows -v
    library torrent info --incomplete --progress=-2.8% --time-downloading=+15days --time-stalled=+15days --stop --delete-incomplete --move broken --delete-rows -v
    library torrent info --incomplete --no-private --time-downloading=+27days --time-stalled=+27days --stop --delete-incomplete --move broken --delete-rows -v
end
