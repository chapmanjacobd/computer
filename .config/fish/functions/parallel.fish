# Defined interactively
function parallel
    command parallel --joblog ~/.jobs/joblog_(date +%Y-%m-%dT%H%M%S).log $argv
end
