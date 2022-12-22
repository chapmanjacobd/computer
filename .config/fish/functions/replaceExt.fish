function replaceExt --argument file ext
    echo (string split -r -m1 . $file)[1].$ext
end
