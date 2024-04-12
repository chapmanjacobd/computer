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
    #lb wt ~/lb/tax.db -l inf --local-media-only -d-0.8 --keep-dir /mnt/d/check/porn/video/ -pf | xargs -P 20 -I{} rm {}
    #lb wt ~/lb/tax.db -l inf --local-media-only -d-0.8 -pfd

    set audio_dirs ~/d/dump/porn/audio/ ~/d/dump/audio/
    set photo_dirs ~/d/dump/porn/image/ ~/d/dump/image/other/ ~/d/dump/image/other/ ~/d/dump/image/other/

    # ~/d/dump/audio/midi/ && fd -tf -eMID -x mv "{}" "{.}.mid"

    fd . $audio_dirs -epng -ejpg -x rm "{}"
    # fd . $audio_dirs -H -tf -eWEBM -j8 -x fish -c 'mkvextract "{}" tracks 0:"{.}".oga && rm "{}"'
    process_audio $audio_dirs

    for file in (fd -tf -eZIP -eRAR -eEXE -er00 . ~/d/dump/porn/video/ ~/d/dump/video/)
        unar $file
    end

    lb fsadd ~/lb/tax.db --video --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move ~/d/check/porn/video/ ~/d/dump/porn/video/ -v
    fd . /mnt/d/dump/porn/video/ -ejpg -ejpeg -epng -epdf -x lb relmv {} /mnt/d/dump/porn/image/from_video/
    fd . /mnt/d/dump/porn/video/ -emka -em4a -x lb relmv {} /mnt/d/dump/porn/audio/from_video/

    lb fsadd ~/lb/tax_sounds.db --audio --delete-unplayable --process --move ~/d/check/porn/audio/ ~/d/dump/porn/audio/

    lb fsadd ~/lb/video.db --video --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move ~/d/check/video/ ~/d/dump/video/
    lb fsadd ~/lb/audio.db --audio --delete-unplayable --process --move ~/d/check/audio/from_video/ ~/d/dump/video/

    lb fsadd ~/lb/audio.db --audio --delete-unplayable --process --move ~/d/check/audio/ ~/d/dump/audio/

    lb fsadd (tempdb) --move ~/d/check/image/ --process --image ~/d/dump/image/ --delete-unplayable
    lb fsadd (tempdb) --move ~/d/check/video/image/ --process ~/d/dump/image/ --delete-unplayable --io-multiplier 0.2
    lb fsadd (tempdb) --move ~/d/check/porn/image/ --process --image ~/d/dump/porn/image/ --delete-unplayable
    lb fsadd (tempdb) --move ~/d/check/porn/video/image/ --process ~/d/dump/porn/image/ --delete-unplayable --io-multiplier 0.2

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
    mktree.py ~/d/

    set joblog (mktemp)
    for i in (seq 1 $MERGERFS_DISKS)
        for m in /mnt/d$i/*
            echo lb fsadd --filesystem ~/lb/fs/d$i.db "$m"
        end
    end | parallel --shuf --joblog $joblog
    parallel --retry-failed --joblog $joblog -j1
end
