# Defined via `source`
function image
    bfs -type f | grep -E \\.(python3 -c 'from library.utils import consts; print("(" + "|".join(consts.IMAGE_EXTENSIONS) + ")")')\$
end
