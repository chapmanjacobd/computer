# Defined via `source`
function video
    grep -E \\.(python3 -c 'from library.utils import consts; print("(" + "|".join(consts.VIDEO_EXTENSIONS) + ")")')\$
end
