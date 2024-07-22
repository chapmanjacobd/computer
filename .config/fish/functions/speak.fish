# Defined interactively
function speak
    piper --model ~/.local/share/models/piper/en_US-joe-medium.onnx --output-raw | aplay -r 22050 -f S16_LE -t raw -
end
