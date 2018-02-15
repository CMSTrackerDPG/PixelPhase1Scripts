Content of the repository
=========================

This repository keeps small utilities for PixelPhase1 (mainly for debugging purposes)

  
  1. *DeadROCViewer* - script that produces maps with marked desired ROCs inside modules.
  2. *HotPixels* - analyzer that looks for 'hyperreactive' ROCs.
  3. *InefficientDoubleCol* - analyze inefficient double in-ROC columns and noisy single columns.
  4. *NoisyCosmicROCs* - analyze online DQM file to spot single and clustered noisy pixel problems.
  5. *PythonBINReader* - script which takes DQM file as an input, looks for all module level Pixel plots and reads bins' values (bin content reflects activity in a specified module) to produce simple ROOT tree used by TkCommissioner.
  6. *SiPixelPhase1Analyzer* - CMSSW tool to produce Offline Pixel Tracker maps which layout resambles real detector.
  7. *TH2PolyOfflineMaps* - creates Pixel Tracker Maps from DQM module level plots.
  8. *TH2PolyOnlineNamingMaps* - creates reference images which show where each sector/blade/ladder is in the given place of the Pixel Detector.
  9. *TMComparator* - utility to create graphical comparisons between Tracker Maps.
  
More information about scripts is provided inside each script directory.
