# Defined interactively
function ytm.url
    yt-dlp --flat-playlist -I :35 -O original_url $argv
end
