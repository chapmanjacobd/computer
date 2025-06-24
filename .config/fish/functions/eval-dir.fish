function eval-dir
    parallel --plain -j80 --line-buffer eval-file ::: (fd -tf -E '*.disabled' . $argv)
    return 0
end
