function qbt.unseed.old
    servers.ssh library torrents --complete --seeders=+4 --time-stalled=+3days --time-seeding=+70days --stop --move dump --delete-rows -v
    servers.ssh library torrents --time-completed=+48h --complete --no-private --stop --move dump --delete-rows
    # check file existence, prevent ghost seed
    servers.ssh library torrents --no-stopped --no-errored --ul --no-all-exists --seeders=-2 --stop --move dump --delete-rows
    # stop incomplete
    servers.ssh library torrents --incomplete --time-active=+75days --time-unseeded=+90days --delete-incomplete --stop --move broken --tag library-delete -v
    servers.ssh library torrents --incomplete --progress=-2.5% --time-downloading=+20days --time-stalled=+20days --stop --delete-incomplete --move broken --delete-rows -v
    servers.ssh library torrents --incomplete --no-private --time-downloading=+20days --time-stalled=+20days --stop --delete-incomplete --move broken --delete-rows -v
end
