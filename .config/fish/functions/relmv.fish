# Defined interactively
function relmv
    set dest $argv[-1]
    for source in $argv[1..-2]
        set relpath (string replace -- $source $dest "")
        set target_dir (dirname $dest$relpath)
        mkdir -p $target_dir
        mv $source $target_dir/
    end
end
