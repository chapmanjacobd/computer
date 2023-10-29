# Defined interactively
function filter_opts
    set -l filtered_opts
    set -l new_argv

    for opt in $argv
        if string match -r -- '-.*' $opt
            set -a filtered_opts $opt
        else
            set -a new_argv $opt
        end
    end

    set -g argv $new_argv
    echo $filtered_opts
end
