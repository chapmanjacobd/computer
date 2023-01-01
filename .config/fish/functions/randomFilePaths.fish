function randomFilePaths --argument howmany
    files | shuf -n $howmany | sed 's/^\.//' | while read line
        echo (pwd)$line
    end
end
