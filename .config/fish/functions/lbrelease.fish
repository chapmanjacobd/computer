function lbrelease --argument oldver newver
    ~/lb/

    #PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring poetry update
    sed -i "s|$oldver|$newver|" xklb/__init__.py

    echo "All of these things should be assigning to a variable; if updating data use db.conn.execute"
    rg db.execute

    lbformat
    rg -i --no-heading --no-line-number --fixed-strings -j1 ', 0)' | grep -ivE 'coalesce|noqa'
    python -m xklb.readme >.github/README.md
    git reset tests/cassettes/
    git restore tests/cassettes/
    if wipm $newver
        git tag -a v$newver && git push --tags
        pip install --upgrade pip pdm
        pdm lock --group :all
        sleep 400
        python -m pip install --upgrade xklb
        python -m pip install --upgrade xklb
    end
end
