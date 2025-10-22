#BEGIN { FS=OFS="," }
#FNR==1 {
#    fname = FILENAME
#    sub(/\.[^.]+$/,"",fname)
#    for (i=1; i<=NF; i++) {
#        $i = fname "_" $i
#    }
#}
#{ row[FNR] = (NR==FNR ? "" : row[FNR] OFS) $0 }
#END {
#    for (rowNr=1; rowNr<=FNR; rowNr++) {
#        print row[rowNr]
#    }
#}
###
#usage: awk -f tst.awk file1.csv file2.csv; paste -d, file1.csv file2.csv | tail -n +2
BEGIN {
    FS=OFS=","
    for (fileNr=1; fileNr<ARGC; fileNr++) {
        filename = ARGV[fileNr]
        if ( (getline < filename) > 0 ) {
            fname = filename
            sub(/\.[^.]+$/,"",fname)
            for (i=1; i<=NF; i++) {
                $i = fname "_" $i
            }
        }
        row = (fileNr==1 ? "" : row OFS) $0
    }
    print row
    exit
}
