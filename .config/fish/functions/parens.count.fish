# Defined interactively
function parens.count
    perl -ne '$o += () = /\(/g; $c += () = /\)/g; END { print "Open: $o, Closed: $c\n" }' $argv
end
