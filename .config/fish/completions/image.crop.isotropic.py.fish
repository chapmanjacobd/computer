complete -c image.crop.isotropic.py -s o -l output_folder -r -f -a '(__fish_complete_directories)' -d 'Output folder (default: output/)'
complete -c image.crop.isotropic.py -n __fish_is_first_arg -a '(__fish_complete_suffix .jpg .jpeg .png .webp .tif .tiff .bmp)' -d 'Input image'
