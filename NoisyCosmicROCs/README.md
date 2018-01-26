# NoisyCosmicROCs Tool
## What does it do?
Given the cosmic run number the tool accessess online dqm GUI to grab the right DQM file to the localhost. Then it loops over all module level ```digi_occupancy_per_col_per_row_*``` plots to spot noisy Pixels. If the noisy Pixel is found it is saved in the html report from which one can easilly go to the problematic plot in the Online GUI.

The tool always starts with getting the MAXIMUM of the current plot than it is being processed in 3 modes:
1. Simple mode: checks whether the maximum plot value is above ```plotThreshold``` if so the module is being reported.
2. Clustered mode: if  ```pixelsInClusterThreshold``` of immediate neighbours of the maximum bin also exceed ```plotThreshold``` the module appears in report.
3. Scattered cluster mode: if ```scatteredClusterFractionThreshold``` fraction of neighbours in range ```scatteredClusterRadius``` are above ```scatteredClusterThreshold``` than the module is being reported.

All these 3 modes have their own output html report accessible in ```<outputDir>/<run number>/```

If everything goes smoothly at the end of execution the tool removes no longer useful ROOT file.

## Configuration and running
For your own usage and customization you need to modify ```config.py```:

1. You need to have a decrypted version of your Grid Certificate Private Key. [Here is the tutorial how to do it.](https://support.citrix.com/article/CTX122930)
2. Modify ```pathToGlobus```, ```userCertInGlobus``` and ```userKeyInGlobus``` so that they point to your certificate and decrypted version of private key.
3. You can tweak thresholds to your needs.

When you are ready to go simply run ```$ python script.py <run number> ```.

## It is not working
First and above all most important: make sure your private key is decrypted and you have the correct path in ```config.py```.
