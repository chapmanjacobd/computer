#!/bin/bash
set -o pipefail

{
    sleep .05
    printf 'key ctrl+c\n'
    sleep .$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key alt+tab\n'
    sleep .05
    printf 'key ctrl+t\n'
    sleep .005
    printf 'key ctrl+l\n'
    sleep .0$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key ctrl+v\n'
    sleep .$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key enter\n'
    sleep .05
    printf 'key alt+tab\n'
    sleep .05
    printf 'key down\n'
    printf 'key ctrl+c\n'
    sleep .$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key alt+tab\n'
    sleep .05
    printf 'key ctrl+t\n'
    sleep .005
    printf 'key ctrl+l\n'
    sleep .0$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key ctrl+v\n'
    sleep .$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key enter\n'
    sleep .05
    printf 'key alt+tab\n'
    sleep .05
    printf 'key down\n'
    sleep .05
    printf 'key ctrl+c\n'
    sleep .$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key alt+tab\n'
    sleep .05
    printf 'key ctrl+t\n'
    sleep .005
    printf 'key ctrl+l\n'
    sleep .0$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key ctrl+v\n'
    sleep .$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key enter\n'
    sleep .05
    printf 'key ctrl+tab\n'
    sleep .05
    printf 'key ctrl+tab\n'
    printf 'key ctrl+l\n'
    sleep .0$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key ctrl+c\n'
    sleep .05
    printf 'key ctrl+w\n'
    sleep .005
    printf 'key alt+tab\n'
    sleep .05
    printf 'key up\n'
    printf 'key up\n'
    printf 'key right\n'
    printf 'key ctrl+v\n'
    printf 'key down\n'
    printf 'key alt+tab\n'
    sleep .0$[ ( $RANDOM % 6 ) + 7 ]s
    printf 'key ctrl+l\n'
    sleep .05
    printf 'key ctrl+c\n'
    sleep .05
    printf 'key ctrl+w\n'
    sleep .005
    printf 'key alt+tab\n'
    sleep .05
    printf 'key ctrl+v\n'
    printf 'key down\n'
    printf 'key left\n'
} | dotool
