# Tests for seq.n. Run with: fishtape ~/.config/fish/tests/seq.n.fish

function seq_test_pairs
    seq.n $argv | string join '|'
end

@test "prints consecutive pairs" (seq_test_pairs 1 3 10) = '1 4|4 7|7 10'
@test "prints consecutive pairs with an increment of one" (seq_test_pairs 1 1 3) = '1 2|2 3'
@test "stops at the last value reachable by the increment" (seq_test_pairs 1 4 10) = '1 5|5 9'
@test "succeeds when the range has one value" (seq.n 5 1 5; echo $status) = 0
@test "prints nothing when the range has one value" -z (seq_test_pairs 5 1 5)
@test "prints nothing when the range is empty" -z (seq_test_pairs 5 1 3)
