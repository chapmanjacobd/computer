# Defined interactively
function speak
    maxmem10 piper --model ~/.local/share/models/piper/en_US-joe-medium.onnx --output-raw | mpv --demuxer=rawaudio --demuxer-rawaudio-rate=22050 --demuxer-rawaudio-channels=1 --demuxer-rawaudio-format=s16le --no-resume-playback -
end
