# Defined interactively
function dl.ia
    print $argv | parallel --eta -j6 --timeout 800s ia download --source original {} --checksum
end
