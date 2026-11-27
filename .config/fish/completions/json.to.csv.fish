complete -c json.to.csv -f
complete -c json.to.csv -s s -l separator -x -d 'Output CSV separator (default: ,)'
complete -c json.to.csv -s f -l file -r -F -d 'JSON file to read (default: stdin)'
complete -c json.to.csv -s k -l keep-only -d 'Keep only the specified fields'
