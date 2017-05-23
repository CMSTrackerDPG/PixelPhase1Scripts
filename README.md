Content of the repository
=========================

This repository keeps small utilities for PixelPhase1 (mainly for debugging purposes)

  1. *CMSPixelTrackerMap* - web interface for printing Pixel Detector Cabling information.
  2. *DeadROCViewer* - script that produces maps with marked desired ROCs inside modules.
  3. *HotPixels* - analyzer that looks for 'hyperreactive' ROCs.
  4. *PythonBINReader* - script which takes DQM file as an input, looks for all module level Pixel plots and reads bins' values (bin content reflects activity in a specified module) to produce simple ROOT tree used by TkCommissioner.
  5. *SiPixelPhase1Analyzer* - CMSSW tool to produce Offline Pixel Tracker maps which layout resambles real detector.
  6. *TH2PolyOfflineMaps* - creates Pixel Tracker Maps from DQM module level plots.
  7. *TMComparator* - utility to create graphical comparisons between Tracker Maps.
  
More information about scripts is provided inside each script directory.
