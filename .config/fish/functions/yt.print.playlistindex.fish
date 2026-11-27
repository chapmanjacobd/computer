function yt.print.playlistindex --wraps='yt-dlp'
    yt-dlp -I :10 -O playlist_index= $argv
end
