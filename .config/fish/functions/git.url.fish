# Defined via `source`
function git.url --description 'Print web URL for git path(s)'
    function _debug
        if set -q GIT_URL_DEBUG
            echo "$argv" >&2
        end
    end

    set -l force_main 0
    set -l args

    for a in $argv
        switch $a
            case --main
                set force_main 1
            case '*'
                set args $args $a
        end
    end

    if test (count $args) -eq 0
        set args "."
    end

    for path in $args
        if not test -e "$path"
            echo "Error: '$path' does not exist." >&2
            continue
        end

        set -l abs_path (realpath "$path")
        set -l git_root (git -C "$abs_path" rev-parse --show-toplevel 2>/dev/null)
        if test -z "$git_root"
            echo "Error: '$path' is not in a git repo." >&2
            continue
        end

        set -l remote (git -C "$git_root" remote get-url origin 2>/dev/null)
        if test -z "$remote"
            echo "Error: no origin remote." >&2
            continue
        end
        _debug "remote=$remote"

        if test $force_main -eq 1
            for b in main master
                if git -C "$git_root" show-ref --verify --quiet "refs/heads/$b"
                    set branch $b
                    break
                end
            end
            if test -z "$branch"
                set branch (git -C "$git_root" rev-parse --short HEAD 2>/dev/null)
            end
        else
            set branch (git -C "$git_root" rev-parse --abbrev-ref HEAD 2>/dev/null)
            if test "$branch" = HEAD -o -z "$branch"
                set branch (git -C "$git_root" rev-parse --short HEAD 2>/dev/null)
            end
        end

        if test -z "$branch"
            echo "Error: no branch or commit." >&2
            continue
        end

        set -l host ""
        set -l user_repo ""
        set -l base_template ""

        # git@host:user/repo.git
        set -l m (string match -r -g '^git@([^:]+):(.+?)(?:\.git)?$' "$remote")
        if test -n "$m"
            set host $m[1]
            set user_repo $m[2]
            set base_template "https://$host/$user_repo"
        else
            # ssh://git@host/user/repo.git
            set -l m (string match -r -g '^ssh://git@([^/]+)/(.+?)(?:\.git)?$' "$remote")
            if test -n "$m"
                set host $m[1]
                set user_repo $m[2]
                set base_template "https://$host/$user_repo"
            else
                # https://host/user/repo.git
                set -l m (string match -r -g '^(https?)://([^/]+)/(.+?)(?:\.git)?$' "$remote")
                if test -n "$m"
                    set scheme $m[1]
                    set host $m[2]
                    set user_repo $m[3]
                    set base_template "$scheme://$host/$user_repo"
                else
                    echo "Error: unrecognized remote format: $remote" >&2
                    continue
                end
            end
        end

        _debug "host=$host user_repo=$user_repo base=$base_template"

        set -l service github
        if string match -qi '*gitlab*' "$host"
            set service gitlab
        else if string match -qi '*bitbucket*' "$host"
            set service bitbucket
        end

        set -l rel_path (string replace -r "^$git_root/?" "" "$abs_path")
        if test "$abs_path" = "$git_root" -o -z "$rel_path"
            set target root
            set rel_path ""
        else if test -d "$abs_path"
            set target tree
        else
            set target blob
        end

        switch $service
            case gitlab
                switch $target
                    case root
                        set url "$base_template/-/tree/$branch"
                    case tree
                        set url "$base_template/-/tree/$branch/$rel_path"
                    case blob
                        set url "$base_template/-/blob/$branch/$rel_path"
                end

            case bitbucket
                switch $target
                    case root
                        set url "$base_template/src/$branch"
                    case tree blob
                        set url "$base_template/src/$branch/$rel_path"
                end

            case github
                switch $target
                    case root
                        set url "$base_template/tree/$branch"
                    case tree
                        set url "$base_template/tree/$branch/$rel_path"
                    case blob
                        set url "$base_template/blob/$branch/$rel_path"
                end
        end

        echo $url
    end
end
