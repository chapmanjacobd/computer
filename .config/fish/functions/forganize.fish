function forganize
    morganize
    dorganize

    sort --unique ~/mc/tabs | lb clustersort | sponge ~/mc/tabs

    #trash-size
    #trash-empty

    #ulimit -n 10240
    #set joblog (mktemp)
    #for m in /mnt/d(seq 1 $MERGERFS_DISKS)/*
    #    if string match -qv -- '*Seeding*' "$m"
    #        echo library christen -r "$m" -v
    #    end
    #end | parallel --shuf --joblog $joblog
    #parallel --retry-failed --joblog $joblog -j1

    fd -tf -d1 --fixed-strings ? . (cat d/.stignore | grep !/ | sed 's|!/\(.*\)|/home/xk/d/\1/|') -x rename ? '' {}

    lb-refresh
    #lb wt ~/lb/tax.db -l inf --local-media-only -d-0.8 --keep-dir /mnt/d/archive/porn/video/ -pf | xargs -P 20 -I{} rm {}
    #lb wt ~/lb/tax.db -l inf --local-media-only -d-0.8 -pfd

    set audio_dirs ~/d/dump/porn/audio/ ~/d/dump/audio/
    set photo_dirs ~/d/dump/porn/image/ ~/d/dump/image/other/ ~/d/dump/image/other/ ~/d/dump/image/other/

    ~/d/dump/audio/midi/ && fd -tf -eMID -x mv "{}" "{.}.mid"

    fd . $audio_dirs -epng -ejpg -x rm "{}"
    fd . $audio_dirs -H -tf -eWEBM -j8 -x fish -c 'mkvextract "{}" tracks 0:"{.}".oga && rm "{}"'
    process_audio $audio_dirs

    for f in (fd -tf -eWEBM -eMP4 -eMKV -eM4V -eFLV -eAVI -eMPG -eMOV -eWMV -eGIF -E 'gifs/**/*' . ~/d/dump/porn/image/)
        if has_both_audio_video "$f"
            mv "$f" ~/d/dump/porn/video/unsorted/
            continue
        else if has_video "$f"
            mv "$f" ~/d/dump/porn/image/gifs/
            continue
        else
            mv "$f" ~/d/dump/porn/audio/unsorted/
        end
    end

    ~/d/dump/video/other/
    fd -epng -ejpg -egif -x mv {} ~/d/dump/image/other/unsorted/dump/video/other/

    fd . ~/d/dump/porn/video/ ~/d/dump/image/other/ ~/d/dump/porn/image/gifs/ -eGIF -eGIFV -j8 -x bash -c 'ffmpeg -hide_banner -loglevel warning -y  -i "{}" -vcodec libx265 "{.}".mp4 && rm "{}"'

    for dir in $photo_dirs
        $dir
        fd -tf -eWEBP -ePNG -x fish -c 'convert "{}" "{.}.jpg" && rm "{}"'
        fd -eJPEG -x mv "{}" "{.}.jpg"
    end

    ~/d/
    for dir in /mnt/d(seq 1 $MERGERFS_DISKS)/*
        if test -d "$dir"
            "$dir"
            yes | bfs -nohidden -type d -exec bfs -f {} -not -type d -exit 1 \; -prune -ok bfs -f {} -type d -delete \;
        end
    end

    set joblog (mktemp)
    for i in (seq 1 $MERGERFS_DISKS)
        for m in /mnt/d$i/*
            echo lb fsadd --filesystem ~/lb/fs/d$i.db "$m"
        end
    end | parallel --shuf --joblog $joblog
    parallel --retry-failed --joblog $joblog -j1
end
