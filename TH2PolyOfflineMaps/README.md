TH2PolyOfflineMaps
==================

The script which behaviour is very similar to the https://github.com/pjurgielewicz/cmssw/tree/pjAnalyzerBranch/DQM/SiPixelPhase1Analyzer in the *MODE_REMAP* but it additionally produces full Tracker Maps (Barrel + Pixel) in the single image for all module level plots available in the input file.

Moreover it looks for 20 minimum and maximum values in Tracker Map bins and prints them (with a corresponding det ID) in the output text file.

How to use
----------

`python TH2PolyOfflineMaps.py <name of the input file>`

where the run number has to be able to be deducted from the input file name. Supported format is as follows

`*_R000######*` - run number is a 6-digit value

Outputs (maps + text file) are saved inside `.OUT/`.
