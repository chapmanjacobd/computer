complete -c invoice.py -n '__fish_is_nth_token 1' -f -a '(__fish_complete_suffix .tex .j2)' -d 'LaTeX template'
complete -c invoice.py -n '__fish_is_nth_token 2' -f -a '(__fish_complete_suffix .yaml .yml)' -d 'Invoice data'
complete -c invoice.py -n '__fish_is_nth_token 3' -f -a '(__fish_complete_suffix .pdf)' -d 'Output PDF'
