function lbrelease --argument oldver newver
    ~/lb/

    #PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring poetry update
    sed -i "s|$oldver|$newver|" xklb/__init__.py
    pdm lock --group :all

    echo "All of these things should be assigning to a variable; if updating data use db.conn.execute"
    rg db.execute

    lbformat
    python readme.py >README.md
    if wipm $newver
        git tag -a v$newver && git push --tags
        pip install --upgrade pip
        sleep 500
        python3.11 -m pip install --upgrade xklb
        python3.11 -m pip install --upgrade xklb
    end
end
