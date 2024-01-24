# Defined interactively
function lb-refresh
    lb fsadd ~/lb/tax.db --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move ~/d/check/porn/video/ ~/d/dump/porn/video/ -v
    fd . /mnt/d/dump/porn/video/ -ejpg -ejpeg -epng -x lb relmv {} /mnt/d/dump/porn/image/from_video/
    fd . /mnt/d/dump/porn/video/ -emka -x lb relmv {} /mnt/d/dump/porn/audio/from_video/

    # lb fsadd ~/lb/audio.db --audio --delete-unplayable --process --move ~/d/check/audio/music/ ~/d/dump/audio/music/ -v
    lb fsadd ~/lb/tax_sounds.db --audio --delete-unplayable --process --move ~/d/check/porn/audio/ ~/d/dump/porn/audio/ -v

    lb fsadd ~/lb/video.db --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move ~/d/check/video/ ~/d/dump/video/ -v
    fd . /mnt/d/dump/video/ -emp3 -x lb relmv {} /mnt/d/dump/audio/from_video/

    ~/lb/
    for db in video.db tax.db audio.db tax_sounds.db
        b sqlite-utils rebuild-fts $db media
    end
    wait
end
