function eval-repeat-dir
    parallel --plain -j80 --line-buffer --joblog /home/xk/.jobs/joblog_jobs.log eval-repeat ::: (fd -tf . $argv)
end
