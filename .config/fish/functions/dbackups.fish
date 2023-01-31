function dbackups
    wol b8:97:5a:09:b0:be

    while not ssh backup grep -qs '/mnt/d ' /proc/mounts
        sleep 5
        notify-send 'Turn on the backup server'
    end

    for folder in 00_Metadata 01_UNLI 02_Home 10_Consulting 30_Computing 54_Unsorted_Documents 55_Writing 56_Lyrics 59_Library 62_Photos_Keep 63_Sounds_Keep 68_VR_TV_Keep 69_Taxes_Keep 77_Library 78_International_Cinema 79_Cinemagraph 84_MIDI 86_Samples 87_Recordings 88_Music_Theory 89_Albums 92_Patterns 93_BG 94_Cool 95_Memes 96_Weird_History 97_Inspiration 98_Me 99_Art 41_8bit 42_GameCube 42_Wii 50_eBooks 51_Manga 53_Scrapbook_Web 20_Spatial 23_LinkMining 38_Interesting_Repos 39_Backup 52_Receipts 76_Rips 86_Rips BackupRevisions
        dbackup $folder
    end

    ~/
    rsync -ah --files-from=(lt ~/lb/audio.db -w 'play_count > 0' -L inf -p f | sed 's|/mnt/d/||' | psub) /mnt/d/ backup:/mnt/d/

    # ssh backup sudo systemctl poweroff
end
