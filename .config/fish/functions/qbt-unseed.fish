function qbt-unseed
    allpc library torrents --complete --seeders=+4 --time-stalled=+3days --time-seeding=+61days --stop --move processing --delete-rows -v
    # check file existence, prevent ghost seed
    allpc lb torrents --no-stopped --no-errored --ul --no-all-exists --seeders=-2 --stop --move processing --delete-rows
    # stop incomplete
    allpc library torrents --incomplete --time-active=+61days --time-unseeded=+90days --delete-incomplete --stop --move processing-incomplete --tag library-delete -v
    allpc library torrents --incomplete --time-active=+61days --inactive --downloaded=0 --stop --tag library-no-seed -v
end
