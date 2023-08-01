function fdupe
    ~/d/

    set photo_dirs ~/d/61_Photos_Unsorted/ ~/d/96_Weird_History/ ~/d/91_New_Art/ ~/d/98_Me/ ~/d/99_Art/
    for dir in $photo_dirs
        $dir/
        czkawka image -d (pwd) >~/Downloads/(path basename $dir)_dupes
    end

    set audio_dirs ~/d/63_Sounds/ ~/d/81_New_Music/ ~/d/82_Audiobooks/ ~/d/83_ClassicalComposers/ ~/d/85_Inspiration/
    for dir in $photo_dirs
        $dir/
        czkawka music -d (pwd) >~/Downloads/(path basename $dir)_dupes
    end

    set video_dirs ~/d/69_Taxes/ ~/d/71_Mealtime_Videos ~/d/72_Education ~/d/73_Entertainment ~/d/75_MovieQueue ~/d/76_CityVideos
    for dir in $photo_dirs
        $dir/
        czkawka video -d (pwd) >~/Downloads/(path basename $dir)_dupes
    end

end
