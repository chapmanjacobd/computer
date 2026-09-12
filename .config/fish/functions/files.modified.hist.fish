function files.modified.hist --description 'Plot recursive file modification times'
    for dir in $argv
        printf '%s\n' "$dir"
        find -- "$dir" -type f -printf '%T@\n' | lowcharts timehist -w 80
    end
end
