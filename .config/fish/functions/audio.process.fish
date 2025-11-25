# Defined interactively
function audio.process
    fd . $argv -H -tf -eDTS -eAAC -eWAV -eAIF -eAIFF -eFLAC -eAIFF -eM4A -eMP3 -eOGG -eMP4 -eM4B -eWMA -j6 -x library process-audio --split-longer-than 36mins
end
