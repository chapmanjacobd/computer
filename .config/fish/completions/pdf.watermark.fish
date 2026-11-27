complete -c pdf.watermark -s a -x -d 'Rotation angle (default: -20)'
complete -c pdf.watermark -s d -x -d 'Rasterization DPI (default: 300)'
complete -c pdf.watermark -s p -x -d 'Point size (default: 20)'
complete -c pdf.watermark -n '__fish_is_nth_token 2' -f -d 'Watermark message'
