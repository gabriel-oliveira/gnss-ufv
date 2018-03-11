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
# Changes :  
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
      "\n  Usage: rltufv_pcs.pl [-h] yyyy ssss skip\n".
      "\n  yyyy : 4-digit (or 2-digit) year".
      "\n  ssss : 4-character session".
      "\n  -h   : Display this help text\n\n" }

# Create startBPE object
# ----------------------
my $bpe = new startBPE();

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
  die ("Error");
}

__END__

