# Defined interactively
function lb-load
    lb fsadd ~/lb/tax.db --video --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move ~/d/check/porn/video/ ~/d/dump/porn/video/ -v
    lb relmv --ext jpg,jpeg,png,pdf ~/d/dump/porn/video/ /mnt/d/dump/porn/image/from_video/
    lb relmv --ext mka,m4a,mp3 ~/d/dump/porn/video/ /mnt/d/dump/porn/audio/from_video/

    lb fsadd ~/lb/tax_sounds.db --audio --delete-unplayable --process --move ~/d/check/porn/audio/ ~/d/dump/porn/audio/ -v
    lb fsadd ~/lb/tax_sounds.db --audio --delete-unplayable --process --move ~/d/check/porn/audio/from_video/ ~/d/dump/porn/video/

    lb fsadd ~/lb/video.db --video --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move ~/d/check/video/ ~/d/dump/video/ -v

    lb relmv --ext srt,vtt,ass ~/d/dump/porn/video/ ~/d/check/porn/video/
    lb relmv --ext srt,vtt,ass ~/d/dump/video/ ~/d/check/video/

    lb fsadd ~/lb/audio.db --audio --delete-unplayable --process --move ~/d/check/audio/from_video/ ~/d/dump/video/
    lb fsadd ~/lb/audio.db --audio --delete-unplayable --process --move ~/d/check/audio/ ~/d/dump/audio/
end
