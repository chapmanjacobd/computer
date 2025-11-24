# Defined interactively
function fd.date
    fd --older (timecalc $argv[1]' + 1 day' | cut -d' ' -f1) --newer (timecalc $argv[1]' - 1 day' | cut -d' ' -f1) $argv[2..-1]
end
