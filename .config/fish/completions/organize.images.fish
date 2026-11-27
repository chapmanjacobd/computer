complete -c organize.images -f
complete -c organize.images -s f -l folder -r -a '(__fish_complete_directories)' -d 'Input folder containing images'
complete -c organize.images -s l -l labels -r -d 'Possible labels for the images'
