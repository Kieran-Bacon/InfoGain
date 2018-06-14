use strict;

if(@ARGV < 2){
    print "Parameters: ground_truth_triples.txt system_triples.txt\n";
    print "\nThe two files should be aligned so that a sentence appear\nin the  same line number in both files. \nThere can be only one extracted triple for each sentence.\n";
    die("\nError: Insufficient number of arguments.\n");
}

open GOLDEN, "$ARGV[0]";
open SYSTEM, "$ARGV[1]";
open MISTAKES, ">precision_errors.txt";
open MISSING, ">recall_errors.txt";

# Removing header
<SYSTEM>;
<GOLDEN>;

my $correct=0;
my $total_system=0;
my $total_gt=0;

foreach my $line (<SYSTEM>){
    chomp($line);
    
    my ($entity1, $relation, $entity2) = split("\t", $line);
    
    my $gline = <GOLDEN>;
    my ($gentity1, $freebase_relation, $gentity2, $grelation, $gsentence) = split("\t", $gline);
    
    if(($entity1 ne $gentity1 || $entity2 ne $gentity2) && ($entity1 ne $gentity2 || $entity2 ne $gentity1)){
        print "System entity pair: $entity1 -- $entity2\n";
        print "Groung truth entity pair: $gentity1 -- $gentity2\n";
        die("The entity pairs from the ground truth and system extractions do not match. The files are incompatible.\n");
    }
    
    # To be correctly extracted, the system relation
    # must contain the ground truth relation.
    if($relation =~ /\Q$grelation\E/gsi && $grelation ne "---"){
	if($relation ne "---"){
            $correct++;
	}
    }else{


	if($relation ne "---"){
	   print MISTAKES "$entity1\t$relation\t$entity2\t$gsentence\n";
	}elsif($grelation ne "---"){
	   print MISSING "$gline\n";
	}
    }
    
    if($relation ne "---"){
        $total_system++;
    }
    
    if($grelation ne "---"){
    	$total_gt++;
    }
    
}

print "Correct: $correct\n";
print "Total System: $total_system\n";
print "Total Groun Truth: $total_gt\n";

print "Precision: " . sprintf("%.4f",$correct/$total_system) ."\n";
print "Recall: " . sprintf("%.4f",$correct/$total_gt) ."\n";
