import FWCore.ParameterSet.Config as cms 

process = cms.Process("SiPixelPhase1Analyzer")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )
process.source = cms.Source("EmptySource")


# process.source = cms.Source("PoolSource",
  # fileNames = cms.untracked.vstring(
    # # '/store/relval/CMSSW_9_0_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/90X_upgrade2017_realistic_v6-v1/10000/12DD2CF5-C8EC-E611-BF61-0CC47A4C8F08.root'
	# "file:DQM_V0013_R000292154__StreamExpressCosmics__Commissioning2017-Express-v1__DQMIO.root"
  # )
# ) 

MODE_ANALYZE = 0
MODE_REMAP = 1
BASEDIR = "DQMData/Run 292154/PixelPhase1/Run summary/Phase1_MechanicalView/"

process.demo = cms.EDAnalyzer('SiPixelPhase1Analyzer',
								opMode = cms.untracked.uint32(MODE_REMAP),
								src = cms.InputTag("generalTracks"),
								debugFileName = cms.untracked.string("debug.txt"),
								
								remapRootFileName = cms.untracked.vstring("DQM_V0013_R000292154__StreamExpressCosmics__Commissioning2017-Express-v1__DQMIO.root"), #only one input is allowed now
								isBarrelSource = cms.untracked.vuint32(0, 1),
								pathToHistograms = cms.untracked.vstring(
								# BASEDIR + "PXForward/",
								BASEDIR + "PXForward/",
								BASEDIR + "PXBarrel/"
								),
								baseHistogramName = cms.untracked.vstring(
								# "num_clusters_per_PXDisk_per_SignedBladePanel_PXRing",
								"num_digis_per_PXDisk_per_SignedBladePanel_PXRing",
								"num_digis_per_SignedModule_per_SignedLadder_PXLayer"
								)
)

process.p = cms.Path(process.demo)

process.load("Configuration.StandardSequences.GeometryRecoDB_cff")

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '90X_upgrade2017_realistic_v6', '')

# auto:phase1_2017_realistic

# Output root file name:
process.TFileService = cms.Service("TFileService", fileName = cms.string('pixelMaps.root') )

# MessageLogger:
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = 'INFO'
process.MessageLogger.categories.append('Analyzer')