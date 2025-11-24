# Defined interactively
function yt.head
    yt-dlp --downloader ffmpeg --skip-download --print-traffic $argv
end
