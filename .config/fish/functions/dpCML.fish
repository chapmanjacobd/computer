# Defined interactively
function dpCML --argument file
    set DATETIME (string split '/' $file -f 2 | string replace 'linkmap_' '' | string replace '.dat' '')
    set DATE (string match -r '\d{8}' $DATETIME)
    set TIME (string sub --start 9 --length 5 $DATETIME)
    head -1 $file | sed 's|\(^.*$\)|date,time,\1|'
    tail -n +2 $file | grep -v '# Ordinary kriging interpolation. Predefined sill, range, and nugget.' \
        | sed "s|\(^.*\$\)|$DATE,$TIME,\1|"
end
