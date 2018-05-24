#!/usr/bin/perl

# ============================================================================
#
# Name    :  rltufv_pcs.pl
#
# Purpose :  Start RLT_UFV BPE process for a particular session
#
# Author  :  GABRIEL DINIZ
# Created :  03-Mar-2018
#
# Changes :  22-mai-2018 add new args
#
# ============================================================================
use strict;

use lib $ENV{BPE};
use startBPE;
use bpe_util;

# Check arguments
# ---------------
if (lc($ARGV[0]) eq "-h") {
  die "\n  Start RLT_UFV BPE process for a particular session\n".
      "\n  Usage: rltufv_pcs.pl [-h] yyyy ssss [arg1 value1 arg2 value2 ...]\n".
      "\n  yyyy : 4-digit (or 2-digit) year".
      "\n  ssss : 4-character session".
      "\n  -h   : Display this help text\n\n" }

if (scalar(@ARGV)%2) {
  die("O número de argumentos deve ser um número par. \n [-h] para ajuda")
}

# Set new user variables
my %varArgs;
%varArgs = (V_BLQINF => 'SYSTEM') if (-s 'E:\\Sistema\\GPSDATA\\DATAPOOL\\REF52\\SYSTEM.BLQ');

if (scalar(@ARGV)>2) {
  for (my $var = 2; $var < scalar(@ARGV); $var+=2) {
    $varArgs{$ARGV[$var]} = $ARGV[$var+1];
  }
}

# Create startBPE object
# ----------------------
my $bpe = new startBPE(%varArgs);

# Redefine mandatory variables
# ----------------------------
$$bpe{PCF_FILE}     = "RLT_UFV";
$$bpe{CPU_FILE}     = "USER";
$$bpe{BPE_CAMPAIGN} = "SYSTEM";
$$bpe{YEAR}         = $ARGV[0];
$$bpe{SESSION}      = $ARGV[1];
$$bpe{SYSOUT}       = "RLT_UFV";
$$bpe{STATUS}       = "RLT_UFV.RUN";
$$bpe{TASKID}       = "RL";


# Reset CPU file
# --------------
$bpe->resetCPU();

# The BPE runs
# ------------
$bpe->run();

# Check for error
# ---------------
if ($$bpe{ERROR_STATUS} ) {
  die ("Error\n");
}

__END__
