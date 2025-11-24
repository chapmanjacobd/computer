function folder.eval
    parallel --plain -j80 --line-buffer file.eval ::: (fd -tf -E '*.disabled' . $argv)
    return 0
end
