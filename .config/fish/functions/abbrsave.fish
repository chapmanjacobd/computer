# Defined interactively
function abbrsave
    abbr -a -- $argv[1] $argv[2..-1]

    file.lines.filter $__fish_config_dir/abbreviations "abbr -a -- $argv[1] "
    echo abbr -a -- $argv[1] (string escape -- $argv[2..-1]) >>$__fish_config_dir/abbreviations
end
