# Defined interactively
function file.urls.titles.preserve
    for p in (modified.staged | grep -i .list)
        ~/bin/preserve_titles.awk $p | sponge $p
    end
end
