function qbt-unseed
    allpc library torrents --complete --seeders=+4 --time-stalled=+3days --time-seeding=+61days --stop --move processing --delete-rows -v
    # stop incomplete
    allpc library torrents --incomplete --time-active=+61days --time-unseeded=+90days --delete-incomplete --stop --move processing-incomplete --tag library-delete -v
    allpc library torrents --incomplete --time-active=+61days --inactive --downloaded=0 --stop --tag library-no-seed -v
end
