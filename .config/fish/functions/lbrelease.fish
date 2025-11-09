function lbrelease --argument newver
    ~/lb/
    set oldver (awk -F'"' '/^__version__/{print $2}' library/__main__.py)

    #PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring poetry update
    sed -i "s|$oldver|$newver|" library/__main__.py

    echo "All of these things should be assigning to a variable; if updating data use db.conn.execute"
    rg db.execute

    ruff check . --select A001 --select A002 --select S110
    lbformat

    rg -i --no-heading --no-line-number --fixed-strings -j1 ', 0)' | grep -ivE 'coalesce|noqa'
    python -m library.readme >.github/README.md
    # git reset tests/cassettes/
    # git restore tests/cassettes/

    git add .
    rg -i --no-heading todo:
    git --no-pager diff "v$oldver"
    git --no-pager diff "v$oldver" | grep TODO
    git diff --stat "v$oldver"
    echo
    git status
    if gum confirm --default=no
        allpc pip install --upgrade pip
        pip install --upgrade pip pdm
        pdm lock --group deluxe,test
        git commit -m "$newver"
        git pull
        git push
        git tag -a "v$newver" && git push --tags
        syncpcs
    else
        return 1
    end
end
