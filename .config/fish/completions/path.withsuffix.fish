complete -c path.withsuffix -s e -l ext -x -d 'Force the output extension'
complete -c path.withsuffix -n '__fish_is_nth_token 1' -x -d 'Suffix to insert'
complete -c path.withsuffix -n '__fish_is_nth_token 2' -F -d 'Input path'
