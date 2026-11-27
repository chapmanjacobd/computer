complete -c ps_mem -f
complete -c ps_mem -l version -d 'Show version'
complete -c ps_mem -s s -l split-args -d 'Separate by all command line arguments'
complete -c ps_mem -s t -l total -d 'Show only the total value'
complete -c ps_mem -s d -l discriminate-by-pid -d 'Show by process rather than by program'
complete -c ps_mem -s S -l swap -d 'Show swap information'
complete -c ps_mem -s p -x -d 'Only show memory usage for these PIDs'
complete -c ps_mem -s w -x -d 'Measure and show memory every N seconds'
