# Tests for hr. Run with: fishtape ~/.config/fish/tests/hr.fish

@test "spans the requested width" (hr --width 10) = '──────────'
@test "accepts a short width flag" (hr -w 4) = '────'
@test "uses the given character" (hr --width 5 --char =) = '====='
@test "centers a label" (hr --width 21 TITLE) = '─────── TITLE ───────'
@test "gives the odd extra column to the right side" (hr --width 20 TITLE) = '────── TITLE ───────'
@test "joins multiple label words" (hr --width 11 a b) = '─── a b ───'
@test "prints a long label without a rule" (hr --width 5 'a long label') = 'a long label'
@test "keeps a label that exactly fits" (hr --width 3 abc) = abc
@test "rejects a multi-character rule character" (hr --width 5 --char ab 2>/dev/null; echo $status) = 1
@test "rejects a non-numeric width" (hr --width abc 2>/dev/null; echo $status) = 1
@test "rejects a zero width" (hr --width 0 2>/dev/null; echo $status) = 1

set --global hr_test_bin (mktemp -d)
mkdir -p $hr_test_bin/good $hr_test_bin/bad
printf '#!/bin/sh\necho 42\n' >$hr_test_bin/good/tput
printf '#!/bin/sh\necho not-a-number\n' >$hr_test_bin/bad/tput
chmod +x $hr_test_bin/good/tput $hr_test_bin/bad/tput

function hr_test_with_tput --argument-names dir
    set -lx PATH $dir $PATH
    hr
end

@test "uses the terminal width by default" (hr_test_with_tput $hr_test_bin/good | string length) = 42
@test "falls back to 80 columns when tput is unusable" (hr_test_with_tput $hr_test_bin/bad | string length) = 80

rm -rf $hr_test_bin
