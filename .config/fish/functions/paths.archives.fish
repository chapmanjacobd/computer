# Defined interactively
function paths.archives
    grep -iE \\.(python3 -c 'from library.utils import consts; print("(" + "|".join(consts.ARCHIVE_EXTENSIONS) + ")$")')
end
