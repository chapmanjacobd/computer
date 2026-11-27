complete -c path.allocator -f
complete -c path.allocator -n '__fish_is_nth_token 2' -a '(__fish_complete_directories)' -d 'Directory to scan'
