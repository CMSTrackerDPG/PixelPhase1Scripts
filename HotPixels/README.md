HotPixels
=========

This tool was developed to identify 'hot pixels' inside each Pixel Detector module based on cosmic DQM. 

Input and how to run
--------------------

`python HotPixelsScript.py <DQM File>`

where the `<DQM_file>` has to be a standard DQM Online file for the Phase 1 (i.e DQM_V0001_PixelPhase1_R000293673.root). You can get such file run by run using the GUI at this address https://cmsweb.cern.ch/dqm/online/data/browse

How it works
------------

The script looks for all plots under the path: `DQMData/Run <runNum deducted from input file name>/PixelPhase1/Run summary/Phase1_MechanicalView` which name starts with `digi_occupancy_per_col_per_row_`.

These plots present data for a given Pixel module which name is right after the `digi_occupancy_per_col_per_row_`.

If there is any bin in the plot which value is * >= 4 * the corresponding pixel is considered as hot and than its ROC number as well as coordinates inside the ROC are calculated.

There are 16 ROCs inside the module organized in 2 x 8 matrix (rows x cols) numbered from 0 to 15. Each ROC is a matrix of 80 x 52 pixels (rows x cols) with (row, col) coordinates starting from (0, 0). To see exactly how ROCs are organized see 'ROCOrganization.png'

As an output `hotpixels_<runNum>.out` text file is created which presents all information required to identify hot pixels. This information is grouped by layer/disk number for example:
  - *B2*: hot pixels from 2nd layer of Barrel detector,
  - *F-1*: hot pixel from -1st disk of Forward detector.
The format of this information is as follows:

`$1, [modCoord: ($2, $3); roc=$4 rocCoord: ($5, $6)] : $7`
  1. Module name
  2. X in module coordinates
  3. Y in module coordinates
  4. Identified ROC number
  5. X in ROC coordinates
  6. Y in ROC coordinates
  7. Value of the hot pixel
  
Beware
------
Whole Pixel Detector consists of 1856 modules. Each of them has 16 80 x 52 ROCs. That is why some patience is required when the script is running (lxplus machines need about 3 minutes to present final result).
