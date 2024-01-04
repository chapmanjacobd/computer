function fdupe
    ~/d/

    set photo_dirs ~/d/dump/porn/image/ ~/d/96_Weird_History/ ~/d/dump/image/other/ ~/d/sync/self/portraits/ ~/d/99_Art/
    for dir in $photo_dirs
        $dir/
        czkawka image -d (pwd) >~/Downloads/(path basename $dir)_dupes
    end

    PATH= /home/xk/.local/bin/lb czkawka-dedupe ~/Downloads/61_Photos_Unsorted_dupes --all-left

    set audio_dirs ~/d/dump/porn/audio/ ~/d/dump/audio/ ~/d/dump/audio/audiobooks/
    for dir in $audio_dirs
        $dir/
        czkawka music -d (pwd) >~/Downloads/(path basename $dir)_dupes
    end

    set video_dirs ~/d/dump/porn/video/ ~/d/71_Mealtime_Videos ~/d/72_Education ~/d/73_Entertainment ~/d/75_Moviequeue
    for dir in $video_dirs
        $dir/
        czkawka video -d (pwd) >~/Downloads/(path basename $dir)_dupes
    end

end
