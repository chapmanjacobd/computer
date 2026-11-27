# Tests for branchname. Run with: fishtape ~/.config/fish/tests/branchname.fish

@test "keeps a name without spaces" (branchname plain) = plain
@test "replaces the first space with a slash" (branchname 'fix the bug') = fix/the-bug
@test "keeps an existing slash" (branchname 'feature/x y') = feature/x/y
@test "replaces later spaces with dashes" (branchname 'a b c') = a/b-c
@test "replaces consecutive spaces with a dash after the first" (branchname 'a  b c') = a/-b-c
@test "prints nothing for an empty name" -z (branchname '')
