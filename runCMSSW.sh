#!/bin/bash

# cmsenv

CMSSW_BASE=/afs/cern.ch/cms/tracker/sistrcalib/MonitorConditionDB/CMSSW_9_0_0

export SCRAM_ARCH=slc6_amd64_gcc530
source /afs/cern.ch/cms/cmsset_default.sh
# echo $SCRAM_ARCH
# echo $HOSTNAME

cd $CMSSW_BASE/src

eval `scramv1 runtime -sh`
# echo $SCRAM_ARCH
# echo $LD_LIBRARY_PATH
# echo $OLDPWD
cd $OLDPWD

GT="90X_upgrade2017_realistic_v6"
RUN_COMMAND="cmsRun ${CMSSW_BASE}/src/DQM/SiPixelPhase1CablingAnalyzer/python/ConfFile_cfg.py globalTag=$GT"
$RUN_COMMAND
