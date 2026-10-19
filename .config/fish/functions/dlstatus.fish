# Defined interactively
function dlstatus
    for db in $argv
        echo $db
        lb database download status $db
        echo
    end

    # for db in $argv
    #    echo $db
    #    lb play video -w time_downloaded\>(timestamp 24 hours ago) -pa $db
    # end

    # for db in $argv
    #    echo $db
    #     lb database history --freqency weekly downloaded $db
    # end

    # lsodl
end
