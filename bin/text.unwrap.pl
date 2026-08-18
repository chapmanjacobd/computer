#!/usr/bin/perl

use strict;
my $pont=qr{[.!?]+};                   ## pontuation
my $abrev=qr{\b(?:Pr|Dr|Mr|[A-Z])\.};  ## abreviations

$/="";   

while(<>){ chomp;                      ## for each paragraph,

  s/\h*\n\h*/ /g;                      ## remove \n
  s/($pont)\h+(\S)/$1\n$2/g;           ## pontuation+space
  s/($abrev)\n/$1 /g;                  ## undo \n after abreviations

  print "$_\n\n";
}