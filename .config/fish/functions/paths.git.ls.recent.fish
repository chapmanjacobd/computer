# Defined interactively
function paths.git.ls.recent
    git log --pretty=format:"DATE:%aI" --name-only | awk '/^DATE:/ {date=substr($0, 6); next} $0!="" && !seen[$0]++ {print date, $0}'
end
