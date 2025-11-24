# Defined interactively
function mam.db.dl --argument db
    sqlite --no-headers --raw-lines "$db" "select distinct path from media where unixepoch(added) > $(timestamp 1 week ago 0 -u) and vip=1 and seeders>0 and my_snatched=0" | parallel -S backup -j1 ".local/data/rtorrent/watch/vip_new/; curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid={}; sleep 2"
    sqlite --no-headers --raw-lines "$db" "select distinct path from media where unixepoch(added) > $(timestamp 1 week ago 0 -u) and vip=0 and seeders>0 and my_snatched=0" | parallel -S backup -j1 ".local/data/rtorrent/watch/nonvip_new/; curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid={}; sleep 2"
    sqlite --no-headers --raw-lines "$db" "update media set my_snatched=1, time_downloaded=unixepoch() where seeders>0 and my_snatched=0 and unixepoch(added) > $(timestamp 1 week ago 0 -u)"
end
