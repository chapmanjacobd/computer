function fileSuffix
    set filen (string split -r -m1 . "$argv[1]")[1]
    set filext (string split -r -m1 . "$argv[1]")[2]
    echo $filen.$argv[2].$filext
end
