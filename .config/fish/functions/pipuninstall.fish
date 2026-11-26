# Defined interactively
function pipuninstall --wraps='pip uninstall'
    set --local force 0
    set --local pip_args
    for arg in $argv
        switch $arg
            case --force -f
                set force 1
            case '*'
                set --append pip_args $arg
        end
    end

    set --local registry ~/.github/pip_installed
    set --query PIPUNINSTALL_REGISTRY
    and set registry $PIPUNINSTALL_REGISTRY

    set --local packages
    for arg in (string match --invert -- '-*' $pip_args)
        set --append packages (string replace --regex '[<>=!~].*$' '' -- $arg)
    end

    set --local references
    if set --query packages[1]
        set references (_pipuninstall_refs $packages)
    end

    if set --query references[1]
        printf 'These packages are referenced elsewhere:\n\n'
        printf '  %s\n' $references
        printf '\n'
        if test $force = 0; and not set --query PIPUNINSTALL_ASSUME_YES
            if not status is-interactive
                echo 'Refusing to uninstall non-interactively. Re-run with --force to skip this check.' >&2
                return 1
            end
            read --local --prompt 'Continue with uninstall? [y/N] ' answer
            if not string match --quiet --regex '^[yY]' -- "$answer"
                echo 'Aborted.' >&2
                return 1
            end
        end
    end

    for package in $packages
        file.lines.filter $registry $package
    end

    pip uninstall -y $pip_args
end
