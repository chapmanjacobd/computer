# Defined interactively
function fdopen --argument prog
    for f in (fd -tf $argv[2..-1])
        $prog $f
    end
end
