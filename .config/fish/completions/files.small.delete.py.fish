complete -c files.small.delete.py -l max-size-mb -x -d "Maximum size for a 'small' file in MB (default: 1.0)"
complete -c files.small.delete.py -l max-dir-size-mb -x -d 'Skip directories larger than this in MB (default: 5.0)'
complete -c files.small.delete.py -f -a '(__fish_complete_directories)' -d 'Directory to clean'
