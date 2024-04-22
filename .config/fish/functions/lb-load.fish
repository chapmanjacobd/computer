# Defined interactively
function lb-load

    lb fsadd ~/lb/tax.db --video --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move ~/d/check/porn/video/ ~/d/dump/porn/video/ -v
    fd . /mnt/d/dump/porn/video/ -ejpg -ejpeg -epng -epdf -x lb relmv {} /mnt/d/dump/porn/image/from_video/
    fd . /mnt/d/dump/porn/video/ -emka -em4a -x lb relmv {} /mnt/d/dump/porn/audio/from_video/

    lb fsadd ~/lb/tax_sounds.db --audio --delete-unplayable --process --move ~/d/check/porn/audio/ ~/d/dump/porn/audio/

    lb fsadd ~/lb/video.db --video --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move ~/d/check/video/ ~/d/dump/video/
    lb fsadd ~/lb/audio.db --audio --delete-unplayable --process --move ~/d/check/audio/from_video/ ~/d/dump/video/

    lb fsadd ~/lb/audio.db --audio --delete-unplayable --process --move ~/d/check/audio/ ~/d/dump/audio/
end
