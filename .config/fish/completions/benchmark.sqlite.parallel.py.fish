complete -c benchmark.sqlite.parallel.py -f
complete -c benchmark.sqlite.parallel.py -l executor -x -a 'thread process' -d 'Executor type'
complete -c benchmark.sqlite.parallel.py -l rows -x -d 'Rows to read from each database'
complete -c benchmark.sqlite.parallel.py -l dbs -x -d 'Number of SQLite databases to use'
