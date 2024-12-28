# Defined interactively
function yt.headers
    yt-dlp --downloader ffmpeg --skip-download --print-traffic $argv
end
