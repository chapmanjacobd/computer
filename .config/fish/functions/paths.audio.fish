# Defined via `source`
function paths.audio
    grep -E \\.(python3 -c 'from library.utils import consts; print("(" + "|".join(consts.AUDIO_ONLY_EXTENSIONS) + ")")')\$
end
