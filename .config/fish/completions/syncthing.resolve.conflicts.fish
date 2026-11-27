complete -c syncthing.resolve.conflicts -f
complete -c syncthing.resolve.conflicts -s h -l help -d 'Show help'
complete -c syncthing.resolve.conflicts -s v -s V -l version -d 'Show version'
complete -c syncthing.resolve.conflicts -s d -l directory -r -a '(__fish_complete_directories)' -d 'Search this directory'
complete -c syncthing.resolve.conflicts -s f -l find -d 'Use find instead of locate'
complete -c syncthing.resolve.conflicts -s o -l output -d 'Only print conflicts'
complete -c syncthing.resolve.conflicts -l nocolor -d 'Disable colored output'
