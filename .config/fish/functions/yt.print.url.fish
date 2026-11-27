# Defined interactively
function yt.print.url --wraps='yt-dlp'
    yt-dlp --flat-playlist -I :35 -O original_url $argv
end
