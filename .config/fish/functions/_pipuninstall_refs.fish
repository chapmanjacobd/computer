function _pipuninstall_refs --description 'Report installed packages and fish config that reference the given pip packages'
    set --local packages $argv
    set --query packages[1]
    or return 0

    set --local fish_dir ~/.config/fish
    set --query PIPUNINSTALL_FISH_DIR
    and set fish_dir $PIPUNINSTALL_FISH_DIR

    # Distribution and console script names never contain spaces, so a single
    # space is an unambiguous field separator here.
    set --local metadata (
        pip show --files $packages 2>/dev/null | awk '
            /^Name: / { package = substr($0, 7); in_files = 0; next }
            /^Required-by: / {
                required_by = substr($0, 14)
                if (required_by != "" && package != "") {
                    count = split(required_by, names, ", ")
                    for (i = 1; i <= count; i++) print "reverse-dependency", names[i], package
                }
                next
            }
            /^Files:$/ { in_files = 1; next }
            /^---$/ { in_files = 0; package = ""; next }
            in_files {
                path = $0
                sub(/^[ \t]+/, "", path)
                if (path ~ /(^|\/)bin\//) {
                    script = path
                    sub(/.*\//, "", script)
                    if (script != "") print "script", package, script
                }
            }
        ' | sort --unique
    )

    set --local scripts
    for line in $metadata
        set --local fields (string split --max 2 ' ' $line)
        switch $fields[1]
            case reverse-dependency
                echo "reverse-dependency: $fields[2] requires $fields[3]"
            case script
                set --append scripts $fields[2] $fields[3]
        end
    end

    set --query scripts[1]
    or return 0

    set --local search_paths $fish_dir/functions $fish_dir/conf.d $fish_dir/completions $fish_dir/config.fish
    set --local existing_paths
    for path in $search_paths
        test -e $path
        and set --append existing_paths $path
    end
    set --query existing_paths[1]
    or return 0

    while set --query scripts[1]
        set --local package $scripts[1]
        set --local script $scripts[2]
        set --erase scripts[1..2]
        set --local matches (
            grep --recursive --line-number --word-regexp --fixed-strings --only-matching \
                -- $script $existing_paths 2>/dev/null | sort --unique
        )
        for match in $matches
            set --local parts (string split --max 2 ':' $match)
            echo "fish-reference: $parts[1]:$parts[2] references '$script' (provided by $package)"
        end
    end
end
