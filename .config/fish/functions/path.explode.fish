function path.explode --description 'Return filename, ext, and directory from the path'
    set -l input $argv[1]
    set -l name (path basename -- $input)
    set -l ext (path extension -- $name)
    set -l root $name
    if test -n "$ext"
        set root (string replace -r -- '\.[^.]*$' '' $name)
        set ext (string replace -r '^\.' '' -- $ext)
    end

    printf '%s\n%s\n%s\n' $root $ext (path dirname -- $input)
end
