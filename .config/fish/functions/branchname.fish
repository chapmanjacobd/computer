# Defined via `source`
function branchname
    # Replace the first space with /
    set -l step1 (string replace -r ' ' '/' -- "$argv")

    # Replace all remaining spaces with -
    set -l result (string replace --all ' ' '-' -- "$step1")

    echo $result
end
