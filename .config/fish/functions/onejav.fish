# Defined interactively
function onejav
    ~/.local/data/onejav/
    fd '\(' -x rm
    python -- ~/bin/torrent_size.py -r *_2.torrent

    set files (fd --max-results 50)
    dragondrop --on-top --all-compact $files
    trash $files
end
