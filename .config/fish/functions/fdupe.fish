function fdupe
    ~/d/
    fd rmlint -x rm

    set audio_dirs ~/d/63_Sounds/ ~/d/81_New_Music/ ~/d/82_Audiobooks/ ~/d/83_ClassicalComposers/ ~/d/85_Inspiration/

    for dir in $audio_dirs
        if not test -e $dir/rmlint.sh
            $dir/
            # for size in 0-1M 1M-10M 10M
            rmlint --match-extension --progress --xattr # --size $size
            bash rmlint.sh -d && rm rmlint.json
            # end
        end
    end

    set photo_dirs ~/d/61_Photos_Unsorted/ ~/d/96_Weird_History/ ~/d/91_New_Art/ ~/d/98_Me/ ~/d/99_Art/
    for dir in $photo_dirs
        $dir/
        cbird -i.algos 1 -update
        yes | cbird -dups -first -select-result -nuke
        # yes | cbird -p.dht 1 -similar -first -select-result -nuke
    end

    ~/d/69_Taxes/
    rmlint --match-extension --progress --xattr --keep-all-tagged ~/d/69_Taxes/ // ~/d/69_Taxes_Keep/
    bash rmlint.sh -d && rm rmlint.json
end
