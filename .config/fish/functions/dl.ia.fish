# Defined interactively
function dl.ia
    print $argv | string replace --all 'https://archive.org/details/' '' | parallel --eta -j6 --timeout 800s ia download --source original {} --checksum
end
