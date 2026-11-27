complete -c cog.validate -s q -d 'Quiet mode'
complete -c cog.validate -l full-check -x -a 'yes no auto' -d 'Check tile/strip leader and trailer bytes'
complete -c cog.validate -a '(__fish_complete_suffix .tif .tiff)' -d 'COG to validate'
