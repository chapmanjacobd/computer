# Defined interactively
function process_audio
    fd . $argv -H -tf -eDTS -eAAC -eWAV -eAIF -eAIFF -eFLAC -eAIFF -eM4A -eMP3 -eOGG -eMP4 -eWMA -j6 -x process_audio.py 
    #if string match -q --ignore-case "*album*" "{.}"; and test (duration "{.}.opus") -gt 2280; split_by_silence "{.}.opus"; end;
end
