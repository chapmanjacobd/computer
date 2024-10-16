function fasd_cd --description 'Function to execute built-in cd'
    # if no $argv, identical with `fasd`
    if test (count $argv) -le 1
        command fasd "$argv"
    else
        command fasd -e 'printf %s' $argv | read -l ret
        test -z "$ret"; and return
        test -d "$ret"; and cd "$ret"; or printf "%s\n" $ret
    end
end
