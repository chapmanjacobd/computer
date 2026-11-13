function audio.to.video.black
    ffmpeg -f lavfi -i color=c=black:s=1280x720:r=5 -i $argv -crf 0 -shortest (path.withsuffix "$argv" '' mp4)
end
