#!/usr/bin/perl
use strict;
use warnings 'all';
use open qw/:std :encoding(utf8)/;
use JSON;
my $prog = "youtube-dl --dump-json --ignore-errors --flat-playlist";
my $chan = "https://www.youtube.com/c/ricksteves";
for ( split /\n/, qx!$prog $chan/playlists! ) {
    for ( decode_json $_) {
        printf "==== %s |%s\n", $_->{url}, $_->{title};
        my $c;
        for ( split /\n/, qx!$prog $_->{url}! ) {

            for ( decode_json $_) {
                printf "%03d|%s|%s\n", ++$c, $_->{id}, $_->{title};
            }
        }
    }
}
