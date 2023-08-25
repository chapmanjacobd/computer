# Defined interactively
function dlstatus --argument db
    lb wt -w time_downloaded\>(timestamp 24 hours ago) -pa $db
    lb ds $db
    lb history --freqency weekly $db downloaded
    # lsodl
end
