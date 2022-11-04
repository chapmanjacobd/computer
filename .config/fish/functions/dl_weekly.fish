function dl_weekly
    mrmusic
    mrvideo
    mrporn
    mrrelax
    morganize

    pip install --upgrade yt-dlp gallery-dl praw xklb

    library tubeupdate ~/lb/audio.db
    library tubeupdate ~/lb/video.db
    #library download ~/lb/video.db --video --small --prefix /mnt/d/
    #library download ~/lb/audio.db --audio --prefix /mnt/d/

    for folder in 61_Photos_Unsorted
        ~/d/$folder/
        gallery-dl --input-file ~/mc/$folder.txt
    end

    dbackups
end
