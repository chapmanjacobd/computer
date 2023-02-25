function genFileCSV
    set ids (seq 0 $argv)
    for id in $ids
        set file "X,Y,id
12.5132783,41.9042869,$id"
        echo $file >(echo $id.csv)
    end
end
