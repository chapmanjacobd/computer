# Defined via `source`
function paths.images
    grep -E \\.(python3 -c 'from library.utils import consts; print("(" + "|".join(consts.IMAGE_EXTENSIONS) + ")")')\$
end
