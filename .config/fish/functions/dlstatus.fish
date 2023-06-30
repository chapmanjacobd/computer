function dlstatus
    echo audio.db
    lb-dev ds ~/lb/audio.db
    echo

    echo video.db
    lb-dev ds ~/lb/video.db
    echo

    echo fs/tax.db
    lb-dev ds ~/lb/fs/tax.db
    echo
end
