# Defined interactively
function dlstatus
    for db in $argv
        echo $db
        lb ds $db
        echo
    end

    # for db in $argv
    #    echo $db
    #    lb wt -w time_downloaded\>(timestamp 24 hours ago) -pa $db
    # end

    # for db in $argv
    #    echo $db
    #     lb history --freqency weekly downloaded $db
    # end

    # lsodl
end
