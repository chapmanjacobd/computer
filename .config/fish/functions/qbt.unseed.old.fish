function qbt.unseed.old
    servers.ssh library torrents --complete --seeders=+4 --time-stalled=+3days --time-seeding=+61days --stop --move processing --delete-rows -v
    # check file existence, prevent ghost seed
    servers.ssh lb torrents --no-stopped --no-errored --ul --no-all-exists --seeders=-2 --stop --move processing --delete-rows
    # stop incomplete
    servers.ssh library torrents --incomplete --time-active=+65days --time-unseeded=+90days --delete-incomplete --stop --move processing-incomplete --tag library-delete -v
    servers.ssh library torrents --incomplete --time-active=+65days --inactive --downloaded=0 --stop --tag library-no-seed -v
end
