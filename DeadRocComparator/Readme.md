The Dead ROC comparator is a tool which show the difference in Dead ROCs between two Online DQM files.
It uses adc ROC level maps (since the digi occupancy in online get reset with a certain frequency, so it could give unmeaningful results)

Usage:
Dowload manually the DQM files (TO BE FIXED, this could be automatic but system and/or user dependent)

./DeadROC_Comparator.py file1 file2 

It will create the following files in the OUT directory:

(text file with list of module names and ROC number)
DeadROC_Diff_Run1-Run2.txt
DeadROC_Run1.txt
DeadROC_Run2.txt

Plus .png images of ROC maps.


