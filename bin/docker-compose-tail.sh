#!/usr/bin/env bash

CR="$(echo -ne '\015')"
tail "$@"  | sed -e "s/${CR}$//" -e "s/^.*${CR}//"