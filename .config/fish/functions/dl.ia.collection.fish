# Defined interactively
function dl.ia.collection
    for collection in $argv
        set -l s (string replace --regex '^https://archive\.org/details/' '' "$collection")
        set s (string split / "$s")[1]
        mkdir "$s"
        ia search "collection:$s" --itemlist | parallel --eta -j6 --timeout 800s ia download --source original {} --checksum --destdir "./$s"
    end
end
