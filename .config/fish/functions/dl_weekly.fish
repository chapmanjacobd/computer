function dl_weekly
    mrmusic
    mrvideo
    mrporn
    mrrelax
    morganize

    pip install --upgrade yt-dlp gallery-dl praw xklb

    tubeupdate
    # dl

    for folder in 61_Photos_Unsorted
        ~/d/$folder/
        gallery-dl --input-file ~/mc/$folder.txt
    end

    dbackups
end
