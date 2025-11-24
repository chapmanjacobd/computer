# Defined interactively
function rpm.size
    rpm -qia | awk '$1=="Name" { n=$3} $1=="Size" {s=$3} $1=="Description" {print s  " " n }' | sort -n | numfmt --to=iec
end
