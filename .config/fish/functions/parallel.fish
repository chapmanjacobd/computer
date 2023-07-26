# Defined interactively
function parallel
    command parallel --joblog ~/.jobs/joblog_(date +%Y%m%d%H%M%S).log $argv
end
