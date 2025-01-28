# Defined via `source`
function video
    bfs -type f | grep -E \\.(python3 -c 'from library.utils import consts; print("(" + "|".join(consts.VIDEO_EXTENSIONS) + ")")')\$
end
