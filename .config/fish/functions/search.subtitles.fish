# Defined interactively
function search.subtitles
    for video in (fd . | fileTypeVideos )
        ffmpeg -i $video -c copy -map 0:s:0 -frames:s 1 -f null - -v 0 -hide_banner
        if test $status = 0
            echo yay
        else
            subliminal --opensubtitles $OPEN_SUBTITLE_CREDENTIALS download -l en "$video"
        end
    end
end
