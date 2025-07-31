# Defined via `source`
function git
    set -l cmd_args $argv

    if test "$cmd_args[1]" = push

        set -l has_force false
        set -l remaining_args
        for arg in $cmd_args[2..-1]
            if test "$arg" = -f -o "$arg" = --force
                set has_force true
            else
                set remaining_args $remaining_args $arg
            end
        end

        if $has_force
            command git pushf $remaining_args
        else
            command git $argv
        end
        return $status
    end

    command git $argv
end
