# Defined interactively
function archives
    bfs -type f | grep -iE \\.(python3 -c 'from library.utils import consts; print("(" + "|".join(consts.ARCHIVE_EXTENSIONS) + ")$")')
end
