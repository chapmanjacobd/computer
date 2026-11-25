# Browse the differences between two directory trees with fzf.
#
#   dirdiff DIR_A DIR_B
#   dirdiff DIR_A              # pick a sibling directory to compare
#   dirdiff                    # pick both directories
#
# Huge files are skipped by default so a folder full of disk images stays
# responsive. Use --all to include them.

function _dirdiff_size --argument-names path
    stat --format=%s -- "$path" 2>/dev/null; or printf '0\n'
end

function _dirdiff_human_size --argument-names bytes
    if command -q numfmt
        numfmt --to=iec-i --suffix=B -- "$bytes" 2>/dev/null
    else
        printf '%s B\n' "$bytes"
    end
end

function _dirdiff_is_text --argument-names path
    test -f "$path"; or return 1
    test -s "$path"; or return 0
    set -l encoding (file --brief --mime-encoding -- "$path" 2>/dev/null)
    test "$encoding" != binary
end

function _dirdiff_text_diff --argument-names left_file right_file display width
    if command -q difft
        difft --color=always --display=$display --width=$width -- "$left_file" "$right_file"
    else if command -q delta
        delta --paging=never -- "$left_file" "$right_file"
    else
        diff -u -- "$left_file" "$right_file" | bat --color=always --style=plain --language=diff 2>/dev/null
        or diff -u -- "$left_file" "$right_file"
    end
end

function _dirdiff_binary_info --argument-names kind rel
    set -l left_file "$DIRDIFF_LEFT/$rel"
    set -l right_file "$DIRDIFF_RIGHT/$rel"

    switch $kind
        case M
            printf 'left:  %s  %s\n' (_dirdiff_human_size (_dirdiff_size "$left_file")) "$left_file"
            printf 'right: %s  %s\n' (_dirdiff_human_size (_dirdiff_size "$right_file")) "$right_file"
            printf '\n'
            file --brief -- "$left_file" "$right_file" 2>/dev/null
            printf '\nfirst differing bytes:\n'
            cmp -l -- "$left_file" "$right_file" 2>/dev/null | head -20
        case L R
            set -l path "$left_file"
            test "$kind" = R; and set path "$right_file"
            printf '%s\n' "$path"
            file --brief -- "$path" 2>/dev/null
            printf '%s\n\n' (_dirdiff_human_size (_dirdiff_size "$path"))
            if command -q xxd
                xxd -l 256 -- "$path" 2>/dev/null
            else
                od -An -tx1 -N256 -- "$path" 2>/dev/null
            end
    end
end

function _dirdiff_one_side_preview --argument-names kind rel
    set -l path "$DIRDIFF_LEFT/$rel"
    test "$kind" = R; and set path "$DIRDIFF_RIGHT/$rel"

    if _dirdiff_is_text "$path"
        bat --color=always --style=numbers --line-range=1:300 -- "$path" 2>/dev/null
        or sed -n '1,300p' -- "$path"
    else
        _dirdiff_binary_info $kind $rel
    end
end

function _dirdiff_preview --argument-names kind rel
    set -l cols 80
    if set -q FZF_PREVIEW_COLUMNS; and test -n "$FZF_PREVIEW_COLUMNS"
        set cols $FZF_PREVIEW_COLUMNS
    end
    set -l width (math $cols - 2)
    set -l left_file "$DIRDIFF_LEFT/$rel"
    set -l right_file "$DIRDIFF_RIGHT/$rel"

    switch $kind
        case M
            if _dirdiff_is_text "$left_file"; and _dirdiff_is_text "$right_file"
                _dirdiff_text_diff "$left_file" "$right_file" inline $width
            else
                _dirdiff_binary_info M "$rel"
            end
        case L R
            _dirdiff_one_side_preview "$kind" "$rel"
    end
end

function _dirdiff_show --argument-names kind rel
    set -l cols (tput cols 2>/dev/null)
    test -n "$cols"; or set cols 100
    set -l width (math $cols - 2)
    set -l left_file "$DIRDIFF_LEFT/$rel"
    set -l right_file "$DIRDIFF_RIGHT/$rel"

    switch $kind
        case M
            if _dirdiff_is_text "$left_file"; and _dirdiff_is_text "$right_file"
                _dirdiff_text_diff "$left_file" "$right_file" side-by-side $width | less -R
            else
                _dirdiff_binary_info M "$rel" | less -R
            end
        case L R
            set -l path "$left_file"
            test "$kind" = R; and set path "$right_file"
            if _dirdiff_is_text "$path"
                bat --paging=always --style=numbers --color=always -- "$path"
                or less -R "$path"
            else
                _dirdiff_binary_info $kind "$rel" | less -R
            end
    end
end

function dirdiff --description 'Browse differences between two directory trees'
    if test (count $argv) -gt 0
        switch "$argv[1]"
            case --_preview
                _dirdiff_preview $argv[2] $argv[3]
                return
            case --_show
                _dirdiff_show $argv[2] $argv[3]
                return
        end
    end

    set -l show_all 0
    set -l paths
    set -l parsing 1

    for arg in $argv
        if test $parsing -eq 0
            set -a paths $arg
            continue
        end

        switch $arg
            case -a --all
                set show_all 1
            case -h --help
                printf '%s\n' \
                    'usage: dirdiff [--all] LEFT RIGHT' \
                    '' \
                    'Browse differing files between two directory trees.' \
                    '  --all  include files larger than 1 MiB' \
                    '' \
                    'With one directory argument, pick its sibling. With none,' \
                    'pick both directories. In fzf: enter opens the diff,' \
                    'ctrl-o opens both trees in meld, esc quits.'
                return 0
            case --
                set parsing 0
            case '-*'
                printf 'dirdiff: unknown option: %s\n' "$arg" >&2
                return 2
            case '*'
                set -a paths $arg
        end
    end

    if test (count $paths) -gt 2
        printf 'dirdiff: expected at most two directories\n' >&2
        return 2
    end

    if test (count $paths) -eq 0
        set -l picked (fd --type d --hidden --exclude .git --max-depth 3 2>/dev/null | fzf --prompt='left directory> ' --height=60% --reverse)
        or return 1
        set paths $picked
    end

    set -l left (realpath -m -- "$paths[1]")
    if test -z "$left"; or not test -d "$left"
        printf 'dirdiff: not a directory: %s\n' "$paths[1]" >&2
        return 2
    end

    if test (count $paths) -eq 1
        set -l parent (dirname -- "$left")
        set -l siblings (fd --type d --hidden --exclude .git --max-depth 1 . "$parent" 2>/dev/null | string replace -r '/$' '')
        set -l choices (printf '%s\n' $siblings | string match -v -- "$left")
        if test (count $choices) -eq 0
            printf 'dirdiff: no sibling directory to compare with %s\n' "$left" >&2
            return 2
        end
        set -l picked (printf '%s\n' $choices | fzf --prompt='right directory> ' --height=60% --reverse)
        or return 1
        set paths[2] $picked
    end

    set -l right (realpath -m -- "$paths[2]")
    if test -z "$right"; or not test -d "$right"
        printf 'dirdiff: not a directory: %s\n' "$paths[2]" >&2
        return 2
    end
    if test "$left" = "$right"
        printf 'dirdiff: both paths are the same directory\n' >&2
        return 2
    end

    # Compare relative paths so the two roots can have different names.
    set -l left_files (find "$left" -type f -printf '%P\n' 2>/dev/null | sort)
    set -l right_files (find "$right" -type f -printf '%P\n' 2>/dev/null | sort)

    set -l common (comm -12 (string join \n -- $left_files | psub) (string join \n -- $right_files | psub))
    set -l only_left (comm -23 (string join \n -- $left_files | psub) (string join \n -- $right_files | psub))
    set -l only_right (comm -13 (string join \n -- $left_files | psub) (string join \n -- $right_files | psub))

    set -l max_size 1048576
    set -l rows
    set -l hidden 0
    set -l identical 0

    for rel in $common
        set -l left_file "$left/$rel"
        set -l right_file "$right/$rel"
        set -l left_size (_dirdiff_size "$left_file")
        set -l right_size (_dirdiff_size "$right_file")
        set -l size $left_size
        test $right_size -gt $size; and set size $right_size

        if test $show_all -eq 0; and test $size -gt $max_size
            set hidden (math $hidden + 1)
            continue
        end
        if cmp -s -- "$left_file" "$right_file"
            set identical (math $identical + 1)
            continue
        end

        set -a rows (string join \t -- M "$rel" (_dirdiff_human_size $size))
    end

    for rel in $only_left
        set -l path "$left/$rel"
        set -l size (_dirdiff_size "$path")
        if test $show_all -eq 0; and test $size -gt $max_size
            set hidden (math $hidden + 1)
            continue
        end
        set -a rows (string join \t -- L "$rel" (_dirdiff_human_size $size))
    end

    for rel in $only_right
        set -l path "$right/$rel"
        set -l size (_dirdiff_size "$path")
        if test $show_all -eq 0; and test $size -gt $max_size
            set hidden (math $hidden + 1)
            continue
        end
        set -a rows (string join \t -- R "$rel" (_dirdiff_human_size $size))
    end

    if test (count $rows) -eq 0
        printf 'No differences'
        test $identical -gt 0; and printf ' (%s identical files ignored)' $identical
        printf '\n'
        return 0
    end

    set -l header 'M differs   L only left   R only right     enter: view   ctrl-o: meld   esc: quit'
    if test $hidden -gt 0
        set header "$header   [$hidden large files hidden, --all to show]"
    end

    set -lx DIRDIFF_LEFT "$left"
    set -lx DIRDIFF_RIGHT "$right"
    set -l meld_cmd "meld "(string escape -- "$left")" "(string escape -- "$right")" >/dev/null 2>&1 &"

    printf '%s\n' $rows | fzf \
        --delimiter='\t' \
        --prompt='diff> ' \
        --header="$header" \
        --preview="fish -c 'dirdiff --_preview \$argv' {1} {2}" \
        --preview-window='right:62%:wrap' \
        --bind="enter:execute(fish -c 'dirdiff --_show \$argv' {1} {2})" \
        --bind="ctrl-o:execute-silent($meld_cmd)" \
        --height=100% \
        --reverse \
        --no-multi
end
