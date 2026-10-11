function lb.release --argument newver
    ~/lb/
    set oldver (awk -F'"' '/^version =/{print $2}' pyproject.toml)

    sed -i -E "s|^version = \"[^\"]+\"|version = \"$newver\"|" pyproject.toml

    echo "All of these things should be assigning to a variable; if updating data use db.conn.execute"
    rg db.execute

    ruff check . --select A001 --select A002 --select S110
    pyformat.all

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
        servers.ssh pip install --upgrade pip
        uv lock
        uv build --no-sources --clear
        git add uv.lock
        git commit -m "$newver"

        git pull
        git push
        git tag -a "v$newver" && git push --tags
        servers.sync
    else
        return 1
    end
end
