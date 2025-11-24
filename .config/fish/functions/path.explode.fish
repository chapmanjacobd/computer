function path.explode --description 'Return filename, ext, and directory from the path'
    echo $argv[1] | sed 's/\(.*\)\/\(.*\)\.\(.*\)$/\2\n\3\n\1/'
end
