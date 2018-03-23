#!/usr/bin/perl

# ============================================================================
#
# Name    :  pppdemo_pcs.pl
#
# Purpose :  Start PPP_DEMO BPE process for a particular session
#
# Author  :  M. Meindl
# Created :  08-Mar-2004
#
# Changes :  11-Aug-2011 RD: Updated for version 5.2
#            24-Jul-2013 SS: $sess replaced by $ARGV[1]
#            08-Mar-2018 Alterado para atender a ApiBerneseUFV]
#                        (Gabriel Diniz de Oliveira)
#            23-Mar-2018 GD: Verifica se arquivo BLQ foi criado pela API
#
# ============================================================================
use strict;

use lib $ENV{BPE};
use startBPE;
use bpe_util;

# Check arguments
# ---------------
if (@ARGV != 2 or lc($ARGV[0]) eq "-h") {
  die "\n  Start PPP_DEMO BPE process for a particular session\n".
      "\n  Usage: pppbas_pcs.pl [-h] yyyy ssss\n".
      "\n  yyyy : 4-digit (or 2-digit) year".
      "\n  ssss : 4-character session".
      "\n  -h   : Display this help text\n\n" }

# Set new user variables
my %varArgs;
%varArgs = (V_BLQINF => 'SYSTEM') if (-s 'E:\\Sistema\\GPSDATA\\DATAPOOL\\REF52\\SYSTEM.BLQ');
	  
# Create startBPE object
# ----------------------
my $bpe = new startBPE(%varArgs);

# Redefine mandatory variables
# ----------------------------
$$bpe{PCF_FILE}     = "PPP_DEMO";
$$bpe{CPU_FILE}     = "USER";
$$bpe{BPE_CAMPAIGN} = "SYSTEM";
$$bpe{YEAR}         = $ARGV[0];
$$bpe{SESSION}      = $ARGV[1];
$$bpe{SYSOUT}       = "PPP_DEM";
$$bpe{STATUS}       = "PPP_DEM.RUN";
$$bpe{TASKID}       = "PD";

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

