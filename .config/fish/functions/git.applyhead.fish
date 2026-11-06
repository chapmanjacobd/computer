# Defined interactively
function git.applyhead --description 'Apply a patch directly to HEAD ignoring dirty working tree'
    if test (count $argv) -eq 0
        echo "Usage: git.applyhead <patch-file>"
        return 1
    end

    set -l patch_file $argv[1]
    if not test -f $patch_file
        echo "Error: Patch file '$patch_file' not found."
        return 1
    end

    # Isolate the index
    set -gx GIT_INDEX_FILE .git/temp-index
    git read-tree HEAD

    if git apply $patch_file
        set -l tree_hash (git write-tree)
        set -l commit_msg "Apply patch: (basename $patch_file)"
        set -l commit_hash (git commit-tree $tree_hash -p HEAD -m "$commit_msg")
        git update-ref HEAD $commit_hash
        echo "Successfully created commit $commit_hash from patch."
    else
        echo "Error: Patch failed to apply cleanly."
    end

    # Clean up environment and temp files
    set -e GIT_INDEX_FILE
    rm -f .git/temp-index
end
