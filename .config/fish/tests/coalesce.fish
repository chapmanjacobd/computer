# Tests for coalesce. Run with: fishtape ~/.config/fish/tests/coalesce.fish

@test "returns the first non-empty value" (coalesce '' '' hello world) = hello
@test "returns the first value when it is not empty" (coalesce hello world) = hello
@test "preserves spaces inside the value" (coalesce '' 'hello world') = 'hello world'

@test "prints nothing when every value is empty" -z (coalesce '' '')
@test "succeeds when every value is empty" (coalesce '' ''; echo $status) = 0
@test "prints nothing without arguments" -z (coalesce)
