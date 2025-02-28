# Defined interactively
function tor-refresh
    for s in pakon backup r730xd len hk
        ssh -t $s qbt_torrents_refresh.py
    end
end
