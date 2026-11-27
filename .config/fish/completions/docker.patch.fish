complete -c docker.patch -f
complete -c docker.patch -n '__fish_is_nth_token 1' -a '(docker image ls --format "{{.Repository}}:{{.Tag}}" 2>/dev/null | string match -v "*<none>*")' -d 'Source image'
