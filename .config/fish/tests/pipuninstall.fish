# Tests for pipuninstall reference checks. Run with: fishtape ~/.config/fish/tests/pipuninstall.fish

set --global pip_test_tmp (mktemp -d)
set --global pip_test_fish_dir $pip_test_tmp/fish
mkdir --parents $pip_test_fish_dir/functions $pip_test_fish_dir/conf.d $pip_test_fish_dir/completions

printf '%s\n' 'function uses_aws' '    aws s3 ls' 'end' >$pip_test_fish_dir/functions/uses_aws.fish
printf '%s\n' 'function uses_awscli_word' '    awscli sync' 'end' >$pip_test_fish_dir/functions/uses_awscli_word.fish
printf '%s\n' 'complete --command aws --no-files' >$pip_test_fish_dir/completions/aws.fish
printf '%s\n' 'set --global unrelated' >$pip_test_fish_dir/conf.d/unrelated.fish
printf '%s\n' 'set --global also_unrelated' >$pip_test_fish_dir/config.fish

set --global --export PIPUNINSTALL_FISH_DIR $pip_test_fish_dir
printf '%s\n' pyyaml catt fakepkg-probe >$pip_test_tmp/pip_installed
set --global --export PIPUNINSTALL_REGISTRY $pip_test_tmp/pip_installed

set --global pip_test_output ''
set --global pip_test_calls

function pip
    set --global --append pip_test_calls (string join ' ' -- $argv)
    if set --query pip_test_output[1]
        printf '%s\n' $pip_test_output
    end
end

function pip_test_reset --argument-names output
    set --global pip_test_output $output
    set --global pip_test_calls
end

# --- _pipuninstall_refs ------------------------------------------------------

pip_test_reset '
Name: pyyaml
Required-by: ansible-core, yamllint'

@test "reports reverse dependencies" (string join '|' (_pipuninstall_refs pyyaml)) = \
    'reverse-dependency: ansible-core requires pyyaml|reverse-dependency: yamllint requires pyyaml'

@test "queries pip metadata with pip show --files" $pip_test_calls[1] = 'show --files pyyaml'

pip_test_reset '
Name: catt
Required-by:
Files:
  ../../../bin/catt
  catt/cli.py'

@test "a console script without fish references produces no output" -z (string join '' (_pipuninstall_refs catt))

pip_test_reset '
Name: awscli
Required-by:
Files:
  ../../../bin/aws
  awscli/__init__.py'

@test "reports fish functions and completions referencing a console script" \
    (string join '|' (_pipuninstall_refs awscli)) = \
    "fish-reference: $pip_test_fish_dir/completions/aws.fish:1 references 'aws' (provided by awscli)|fish-reference: $pip_test_fish_dir/functions/uses_aws.fish:2 references 'aws' (provided by awscli)"

@test "does not match longer words that contain the console script name" \
    -z (string join '' (_pipuninstall_refs awscli) | string match '*uses_awscli_word*')

set --global --export PIPUNINSTALL_FISH_DIR $pip_test_fish_dir/functions

@test "console script 'aws' does not match the word 'awscli'" -z (string join '' (_pipuninstall_refs awscli) | string match '*uses_awscli_word*')

set --global --export PIPUNINSTALL_FISH_DIR $pip_test_fish_dir

pip_test_reset '
Name: pyyaml
Required-by: ansible-core
---
Name: catt
Required-by:
Files:
  ../../../bin/catt
---
Name: awscli
Required-by:
Files:
  ../../../bin/aws'

@test "handles multiple packages in one pip show call" (string join '|' (_pipuninstall_refs pyyaml catt awscli)) = \
    "reverse-dependency: ansible-core requires pyyaml|fish-reference: $pip_test_fish_dir/completions/aws.fish:1 references 'aws' (provided by awscli)|fish-reference: $pip_test_fish_dir/functions/uses_aws.fish:2 references 'aws' (provided by awscli)"

pip_test_reset ''

@test "reports nothing when pip knows nothing about the package" -z (string join '' (_pipuninstall_refs missing-package))

# --- pipuninstall ------------------------------------------------------------

pip_test_reset '
Name: fakepkg-probe
Required-by: realrequirer
Files:
  ../../../bin/aws'

function pip_test_uninstall_called
    string match --quiet '*uninstall*' -- $pip_test_calls
end

pipuninstall fakepkg-probe >/dev/null 2>&1
set --local pipuninstall_status $status

@test "refuses to uninstall with references when stdin is not a terminal" $pipuninstall_status -eq 1
@test "does not call pip uninstall when refusing" (pip_test_uninstall_called; echo $status) = 1
@test "keeps the package in the installed registry when refusing" (string match --quiet fakepkg-probe <$PIPUNINSTALL_REGISTRY; echo $status) = 0

pip_test_reset '
Name: fakepkg-probe
Required-by: realrequirer
Files:
  ../../../bin/aws'

pipuninstall --force fakepkg-probe >/dev/null 2>&1
set --local pipuninstall_forced_status $status

@test "--force uninstalls despite references" $pipuninstall_forced_status -eq 0
@test "--force still calls pip uninstall -y" (pip_test_uninstall_called; echo $status) = 0
@test "--force is not passed through to pip" (string match --quiet -- '*--force*' -- (string join '|' $pip_test_calls); echo $status) = 1
@test "removes the package from the installed registry" (string match --quiet fakepkg-probe <$PIPUNINSTALL_REGISTRY; echo $status) = 1

pip_test_reset ''

pipuninstall --force fakepkg-probe >/dev/null 2>&1

@test "uninstalls without prompting when there are no references" $status -eq 0

rm --recursive --force $pip_test_tmp
