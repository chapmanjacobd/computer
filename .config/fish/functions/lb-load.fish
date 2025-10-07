# Defined interactively
function lb-load
    for file in (fd -tf -eZIP -e7z -eRAR -eEXE -er00 -eCBR -eCBZ -eISO . ~/d/dump/porn/video/ ~/d/dump/video/)
        unardel $file
    end

    for d in /mnt/d(seq 1 10)
        lb fsadd ~/lb/fs/tax.db --video --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move $d/check/porn/video/ $d/dump/porn/video/ -v
        lb mv --ext jpg,jpeg,png,pdf,tiff,tif,bmp,webp $d/dump/porn/video/ $d/dump/porn/image/from_video/
        lb mv --ext mka,m4a,mp3 $d/dump/porn/video/ $d/dump/porn/audio/from_video/

        $d/dump/porn/video/
        fd -edb -edcsv -enfo -x rm

        lb fsadd ~/lb/fs/tax_sounds.db --audio --delete-unplayable --process --move $d/check/porn/audio/ $d/dump/porn/audio/ -v
        lb fsadd ~/lb/fs/tax_sounds.db --audio --delete-unplayable --process --move $d/check/porn/audio/from_video/ $d/dump/porn/video/

        lb fsadd ~/lb/fs/video.db --video --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move $d/check/video/ $d/dump/video/ -v

        lb mv --ext srt,vtt,ass $d/dump/porn/video/ $d/check/porn/video/
        lb mv --ext srt,vtt,ass $d/dump/video/ $d/check/video/

        lb fsadd ~/lb/fs/audio.db --audio --delete-unplayable --process --move $d/check/audio/from_video/ $d/dump/video/
        lb fsadd ~/lb/fs/audio.db --audio --delete-unplayable --process --move $d/check/audio/ $d/dump/audio/

        lb fsadd ~/lb/image.db --move $d/check/image/ --process --image $d/dump/image/ --delete-unplayable -v
        lb fsadd ~/lb/fs/video.db --move $d/check/video/image/ --process $d/dump/image/ --delete-unplayable --threads 3
        lb fsadd ~/lb/fs/tax_image.db --move $d/check/porn/image/ --process --image $d/dump/porn/image/ --delete-unplayable -v
        lb fsadd ~/lb/fs/tax.db --move $d/check/porn/video/image/ --process $d/dump/porn/image/ --delete-unplayable --threads 3

        lb mv --ext mka,mp3,oga,opus $d/check/porn/video/ $d/dump/porn/image/ /mnt/d/dump/porn/audio/from_video/
    end
end
