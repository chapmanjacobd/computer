function dbackups
    wol b8:97:5a:09:b0:be

    while not ssh backup grep -qs '/mnt/d ' /proc/mounts
        sleep 5
        notify-send 'Turn on the backup server'
    end

    for folder in 00_Metadata 02_Home 10_Consulting 30_Computing 54_Unsorted_Documents 55_Writing 56_Lyrics 59_Library 62_Photos_Keep 63_Sounds_Keep 68_Vr_Tv_Keep 69_Taxes_Keep 77_Library 78_International_Cinema 79_Cinemagraph 84_MIDI 86_Samples 87_Recordings 88_Music_Theory 89_Albums 92_Patterns 93_Bg 94_Cool 96_Weird_History 97_Inspiration 98_Me 99_Art 41_8bit 42_Gamecube 42_Wii 50_Ebooks 51_Manga 53_Scrapbook_Web 20_Spatial 23_Linkmining 38_Interesting_Repos 39_Backup 52_Receipts 76_Rips 86_Rips backuprevisions
        dbackup $folder
    end

    ~/
    rsync -ah --files-from=(lb lt ~/lb/audio.db -w 'play_count > 0' -pf | sed 's|/mnt/d/||' | psub) /mnt/d/ backup:/mnt/d/

    # ssh backup sudo systemctl poweroff
end
