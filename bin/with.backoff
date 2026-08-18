#!/bin/bash
# Beware of set -e killing your whole script!

max_attempts=${ATTEMPTS-5}
timeout=${TIMEOUT-800}
attempt=0
exitCode=0

while [[ $attempt < $max_attempts ]]
do
  "$@"
  exitCode=$?

  if [[ $exitCode == 0 ]]
  then
    break
  fi

  echo "Failure! Retrying in $timeout.." 1>&2
  sleep $timeout
  attempt=$(( attempt + 1 ))
  timeout=$(echo "1.4 * $timeout" | bc)
done

if [[ $exitCode != 0 ]]
then
  echo "You've failed me for the last time! ($@)" 1>&2
fi

