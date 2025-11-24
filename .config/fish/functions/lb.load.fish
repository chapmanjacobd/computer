# Defined interactively
function lb.load
    lb unardel -vy ~/d/dump/video/ ~/d/dump/porn/video/

    for d in /mnt/d(seq 1 10)
        lb fsadd ~/lb/fs/tax.db --video --hash --delete-unplayable --check-corrupt --full-scan-if-corrupt 15% --delete-corrupt 20% --move $d/check/porn/video/ $d/dump/porn/video/ -v
        lb mv --ext jpg,jpeg,png,pdf,tiff,tif,bmp,webp $d/dump/porn/video/ $d/dump/porn/image/from_video/
        lb mv --ext mka,m4a,mp3 $d/dump/porn/video/ $d/dump/porn/audio/from_video/

        $d/dump/porn/video/
        fd -edb -edcsv -enfo -x rm

        lb fsadd ~/lb/fs/tax_sounds.db --audio --delete-unplayable --process --move $d/check/porn/audio/ $d/dump/porn/audio/ -v
        lb fsadd ~/lb/fs/tax_sounds.db --audio --delete-unplayable --process --move $d/check/porn/audio/from_video/ $d/dump/porn/video/

        lb fsadd ~/lb/fs/tax_VR.db --delete-unplayable --move $d/check/porn/vr/ $d/dump/porn/vr/ -v

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

    lb fs ~/lb/fs/video.db -w 'video_count=0 and audio_count>=1' -pf | parallel lb relmv {} ~/d/dump/audio/from_video/
    lb fs ~/lb/fs/video.db -w 'video_count>=1 and audio_count=0' -pf | parallel lb relmv {} ~/d/dump/image/gifs/from_video/

    lb fs ~/lb/fs/tax.db -w 'video_count=0 and audio_count>=1' -pf | parallel lb relmv {} ~/d/dump/porn/audio/from_video/
    lb fs ~/lb/fs/tax.db -w 'video_count>=1 and audio_count=0' -pf | parallel lb relmv {} ~/d/dump/porn/image/gifs/from_video/
end
