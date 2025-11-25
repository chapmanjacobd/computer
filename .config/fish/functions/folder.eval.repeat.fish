function folder.eval.repeat
    parallel --plain -j80 --line-buffer --joblog /home/xk/.jobs/joblog_jobs.log file.eval.repeat ::: (fd -tf . $argv)
end
