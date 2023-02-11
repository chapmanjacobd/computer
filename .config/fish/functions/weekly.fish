function weekly
    mrmusic
    #mrvideo
    #mrporn
    #mrrelax
    morganize

    pip install --upgrade yt-dlp gallery-dl praw xklb

    tubeupdate
    dla
    wait

    for folder in 61_Photos_Unsorted
        ~/d/$folder/
        gallery-dl --input-file ~/mc/$folder.txt
    end

    trash ~/d/.stversions/*
    dbackups
end
