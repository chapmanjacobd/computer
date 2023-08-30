# Defined interactively
function dlstatus --argument db
    lb wt -w time_downloaded\>(timestamp 24 hours ago) -pa $db
    lb ds $db
    lb history --freqency weekly downloaded $db
    # lsodl
end
