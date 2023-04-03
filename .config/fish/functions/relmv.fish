# Defined via `source`
function relmv
    set dest $argv[-1]
    for source in $argv[1..-2]
        set abspath (path resolve "$source")
        set trim_len (string length (common_prefix "$abspath" "$dest"))
        set relpath (string sub -s $trim_len "$abspath")
        set target_dir (path normalize (dirname "$dest/$relpath"))
        echo mv "$abspath" "$target_dir/"
    end
end
