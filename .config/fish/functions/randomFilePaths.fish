function randomFilePaths --argument num
    files | shuf -n $num | sed 's/^\.//' | while read line
        echo (pwd)$line
    end
end
