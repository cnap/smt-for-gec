#!/usr/bin/perl

# prints lines where fields 1 and 2 (tab separated) are not equal

$count = 0;

foreach $line (<>) {
    chomp($line);

	@vals = split(/\t/,$line);
	$vals[0] =~ s/^\s+|\s+$//g;
	$vals[1] =~ s/^\s+|\s+$//g;

  if ($vals[0] ne $vals[1]) {
	  print "$vals[0]\t$vals[1]\n";
  }
	$count++;
}
