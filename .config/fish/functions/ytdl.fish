# Defined interactively
function ytdl
    _ytdl --extractor-args "youtube:skip=hls,dash,translated_subs" --extractor-args "youtubetab:skip=authcheck" $argv
    or _ytdl $argv
end
