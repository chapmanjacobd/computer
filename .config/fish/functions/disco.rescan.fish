# Defined interactively
function disco.rescan
    disco.dev add --scan-subtitles audio.db ~/sync/audio/
    disco.dev add books.db ~/sync/text
    disco.dev add images.db ~/sync/image/Screenshots
    disco.dev add --scan-subtitles video.db ~/sync/video
end
