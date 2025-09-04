# Defined interactively
function archives
    grep -iE \\.(python3 -c 'from library.utils import consts; print("(" + "|".join(consts.ARCHIVE_EXTENSIONS) + ")$")')
end
