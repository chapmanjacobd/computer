complete -c duckdb.typecaster -l rows -x -d 'Rows to sample for type inference'
complete -c duckdb.typecaster -l loss -d 'Print records where the type does not match'
complete -c duckdb.typecaster -l force -d 'Use TRY_CAST instead of CAST'
complete -c duckdb.typecaster -n '__fish_is_nth_token 2' -f -d 'Table name to modify'
