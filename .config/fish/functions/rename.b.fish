# Defined interactively
function rename.b
    set old $argv[1]
    set new $argv[2]
    set paths $argv[3..-1]

    for f in $paths
        sed "s|\b$old\b|$new|" -i "$f"
        mv $f (echo $f | sed "s|\b$old\b|$new|")
    end
end
