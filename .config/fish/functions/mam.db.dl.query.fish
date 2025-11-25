# Defined interactively
function mam.db.dl.query --argument db
    load.env.mam

    lb.dev fs "$db" -w 'my_snatched=0' 'seeders>0' $argv[2..-1] -pa

    if confirm
        lb.dev fs "$db" -w 'my_snatched=0' 'seeders>0' 'vip=1' $argv[2..-1] -pf | unique | parallel -S backup -j1 ".local/data/rtorrent/watch/vip_new/; curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid={}; sleep 2"
        lb.dev fs "$db" -w 'my_snatched=0' 'seeders>0' 'vip=1' $argv[2..-1] -pf | sqlite_update.py "$db" media 'my_snatched=1,time_downloaded=unixepoch()' -v

        lb.dev fs "$db" -w 'my_snatched=0' 'seeders>0' 'vip=0' $argv[2..-1] -pf | unique | parallel -S backup -j1 ".local/data/rtorrent/watch/nonvip_new/; curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid={}; sleep 2"
        lb.dev fs "$db" -w 'my_snatched=0' 'seeders>0' 'vip=0' $argv[2..-1] -pf | sqlite_update.py "$db" media 'my_snatched=1,time_downloaded=unixepoch()' -v
    end
end
