# Defined interactively
function killjobs
    for job in (jobs)
        set -l job_id (echo $job | awk '{print $1}')
        set -l job_state (echo $job | awk '{print $4}')

        # Check if the job is still running
        if test "$job_state" = running
            echo "Killing background job: $job_id"
            kill %$job_id
        end
    end
end
