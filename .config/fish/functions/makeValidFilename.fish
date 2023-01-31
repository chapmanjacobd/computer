function makeValidFilename
    sed "s/[^[:alnum:]-]//g"
end
