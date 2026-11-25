#!/bin/bash
set -o pipefail

sleep .005
{
    printf 'key down\n'
    printf 'key delete\n'
    #printf 'key down\n'
    #printf 'key shift+down\n'
} | dotool
