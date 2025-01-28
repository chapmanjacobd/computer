# Defined interactively
function audio
    bfs -type f | grep -E (python3 -c 'from library.utils import consts; print("\\.(" + "|".join(consts.AUDIO_ONLY_EXTENSIONS) + ")")')
end
