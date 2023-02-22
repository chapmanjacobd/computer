function weekly
    trash ~/d/.stversions/*
    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files backup:.local/Downloads/. ~/d/75_MovieQueue/

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

    dbackups
end
