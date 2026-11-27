# Defined interactively
function yt.head --wraps='yt-dlp'
    yt-dlp --downloader ffmpeg --skip-download --print-traffic $argv
end
