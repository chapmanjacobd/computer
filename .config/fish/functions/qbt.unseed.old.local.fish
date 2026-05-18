# Defined in /home/xk/.config/fish/functions/qbt.unseed.old.fish @ line 1, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function qbt.unseed.old.local
    library torrents --complete --seeders=+4 --time-stalled=+3days --time-seeding=+80days --stop --move dump --delete-rows -v
    library torrents --time-completed=+48h --complete --no-private --stop --move dump --delete-rows
    # check file existence, prevent ghost seed
    library torrents --no-stopped --no-errored --ul --no-all-exists --seeders=-2 --stop --move dump --delete-rows
    # stop incomplete
    library torrents --incomplete --time-active=+85days --time-unseeded=+100days --delete-incomplete --stop --move broken --tag library-delete -v
    library torrents --incomplete --progress=-2.8% --time-downloading=+15days --time-stalled=+15days --stop --delete-incomplete --move broken --delete-rows -v
    library torrents --incomplete --no-private --time-downloading=+27days --time-stalled=+27days --stop --delete-incomplete --move broken --delete-rows -v
end
