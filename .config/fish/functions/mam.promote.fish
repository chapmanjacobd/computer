function mam.promote -a max
    load.env.mam

    if test $max -gt 0
        set filled (torrent.promote ~/.local/data/rtorrent/watch/new -n $max | count)
        echo Moved $filled from new/
        set max (math $max-$filled)

        set filled (torrent.promote ~/.local/data/rtorrent/watch/vip_new --reverse -n $max | count)
        echo Moved $filled from vip_new/
        set max (math $max-$filled)

        set filled (torrent.promote ~/.local/data/rtorrent/watch/nonvip_new -n $max | count)
        echo Moved $filled from nonvip_new/
    end
end
