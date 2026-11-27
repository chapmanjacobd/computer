complete -c csv.to.json -f
complete -c csv.to.json -l columns -r -d 'Comma-separated column names'
complete -c csv.to.json -l header -d 'Treat the first row as a header'
complete -c csv.to.json -s d -l delimiter -x -d 'Input delimiter (default: ,)'
complete -c csv.to.json -l sniff -d 'Guess the CSV dialect'
complete -c csv.to.json -n __fish_is_first_arg -r -F -d 'CSV file (default: stdin)'
