complete -c filterfile --condition __fish_is_first_arg --force-files
complete -c filterfile --condition 'not __fish_is_first_arg' --no-files -a '(cat (__fish_first_token))'
