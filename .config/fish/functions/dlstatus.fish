# Defined interactively
function dlstatus
    for db in $argv
        lb wt -w time_downloaded\>(timestamp 24 hours ago) -pa $db
        lb ds $db
        lb history --freqency weekly downloaded $db
    end
    # lsodl
end
