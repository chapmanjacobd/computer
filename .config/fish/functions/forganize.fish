function forganize
    morganize
    dorganize

    sort --unique ~/mc/tabs | lb clustersort | sponge ~/mc/tabs

    #trash-size
    #trash-empty

    set joblog (mktemp)
    for m in /mnt/d(seq 1 $MERGERFS_DISKS)/*
        echo library christen -r "$m" -v
    end | parallel --shuf --joblog $joblog
    parallel --retry-failed --joblog $joblog -j1

    fd -tf -d1 --fixed-strings ? . (cat d/.stignore | grep !/ | sed 's|!/\(.*\)|/home/xk/d/\1/|') -x rename ? '' {}

    lb-refresh
    lb wt ~/lb/fs/tax.db -l inf --local-media-only -d-0.8 --keep-dir /mnt/d/69_Taxes_Keep/ -pf | xargs -P 20 -I{} rm {}
    lb wt ~/lb/fs/tax.db -l inf --local-media-only -d-0.8 -pfd

    set audio_dirs ~/d/63_Sounds/ ~/d/81_New_Music/ ~/d/82_Audiobooks/ ~/d/83_Classical_Composers/ ~/d/85_Inspiration/
    set photo_dirs ~/d/61_Photos_Unsorted/ ~/d/96_Weird_History/ ~/d/94_Cool/ ~/d/93_Bg/ ~/d/91_New_Art/ ~/d/98_Me/ ~/d/99_Art/

    # ~/d/84_MIDI && fd -tf -eMID -x mv "{}" "{.}.mid"

    fd . $audio_dirs -epng -ejpg -x rm "{}"
    fd . $audio_dirs -H -tf -eWEBM -j8 -x fish -c 'mkvextract "{}" tracks 0:"{.}".oga && rm "{}"; if test (duration "{.}.oga") -gt 2280; split_by_silence "{.}.oga"; end'
    process_audio $audio_dirs

    for f in (fd -tf -eWEBM -eMP4 -eMKV -eM4V -eFLV -eAVI -eMPG -eMOV -eWMV -eGIF -E 'gifs/**/*' . ~/d/61_Photos_Unsorted/)
        if has_both_audio_video "$f"
            mv "$f" ~/d/69_Taxes/unsorted/
            continue
        else if has_video "$f"
            mv "$f" ~/d/61_Photos_Unsorted/gifs/
            continue
        else
            mv "$f" ~/d/63_Sounds/unsorted/
        end
    end

    ~/d/71_Mealtime_Videos/
    fd -epng -ejpg -egif -x mv {} ~/d/91_New_Art/unsorted/71_Mealtime_Videos/

    fd . ~/d/69_Taxes/ ~/d/91_New_Art/ ~/d/61_Photos_Unsorted/gifs/ -eGIF -eGIFV -j8 -x bash -c 'ffmpeg -hide_banner -loglevel warning -y  -i "{}" -vcodec libx265 "{.}".mp4 && rm "{}"'

    for dir in $photo_dirs
        $dir
        fd -tf -eWEBP -ePNG -x fish -c 'convert "{}" "{.}.jpg" && rm "{}"'
        fd -eJPEG -x mv "{}" "{.}.jpg"
    end

    ~/d/
    yes | bfs -nohidden -type d -exec bfs -f {} -not -type d -exit 1 \; -prune -ok bfs -f {} -type d -delete \;

    set joblog (mktemp)
    for m in /mnt/d(seq 1 $MERGERFS_DISKS)/*
        echo lb fsadd --filesystem ~/lb/fs/d.db "$m"
    end | parallel --shuf --joblog $joblog
    parallel --retry-failed --joblog $joblog -j1
end
