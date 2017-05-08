#!/bin/env python
import sys
import os
import pickle

from copy import deepcopy

def PrintTracker(pixelCablingInfoDic, trackerMapInputName, trackerMapOutputName, trackerModulesOutput):
  
  with open(trackerMapInputName, "w") as outFile:
    [outFile.write(k + " 0 250 0\n")  for k in pixelCablingInfoDic]
            
  os.system(('print_TrackerMap %s "TrackerMap" %s 2400 False False 999 -999 True')%(trackerMapInputName, trackerMapOutputName))
  
  with open(trackerModulesOutput, "w") as file:
    [file.write( k + "\n") for k in pixelCablingInfoDic]

cablingFileName = "DATA/CablingDB/pxCabl.csv"
detIdDicFileName = "DATA/detids.dat"

outDicTxtFileName = "DATA/log.txt"

pixelCablingInfoDic = {}
pixelCablingInfoDicFed = {}
detIdDic = {}

with open(detIdDicFileName, "r") as inputDic:
  for line in inputDic:
    l = line.strip()
    if len(l) > 0:
      strSpl = l.split()
      detIdDic.update({strSpl[1] : strSpl[0]})

#print(len(detIdDic))

isFirstLine = True
categories = []
categoryNamePositionDic = {}
interestingCategories = ["Official name of position", "CCU", "channel", "FED channel", "FED position", "FED receiver", "FED ID", "FEC/FED crate", "FEC ID", "FEC position"]
with open(cablingFileName, "r") as inputCabl:
  for line in inputCabl:
    strSpl = line.split(",")
    if isFirstLine:
      categories = deepcopy(strSpl)
      for i in range(len(categories)):
        categoryNamePositionDic.update({categories[i].strip() : i}) # assign column number to the column name
      for k in categoryNamePositionDic:
        print(k, categoryNamePositionDic[k])
      isFirstLine = False
    else:
      #onlineModuleName = strSpl[categoryNamePositionDic[interestingCategories[0]]]
      #print(onlineModuleName)

      fedId = strSpl[categoryNamePositionDic["FED ID"]]
      fedCh = strSpl[categoryNamePositionDic["FED channel"]]
      detId = detIdDic[strSpl[categoryNamePositionDic["Official name of position"]]]

      tmpDic = {}
      for item in interestingCategories:
        if item == "Official name of position":
          tmpDic.update({"detId" : detId})
        else:
          tmpDic.update({item.replace("/", " ") : strSpl[categoryNamePositionDic[item]]})

      # DETID DICTIONARY
      pixelCablingInfoDic.update({detId : tmpDic})
      # FED DICTIONARY
      if fedId in pixelCablingInfoDicFed:
        pixelCablingInfoDicFed[fedId].update({fedCh : tmpDic})
      else:
        pixelCablingInfoDicFed.update({fedId : {fedCh : tmpDic}})

# PrintTracker(pixelCablingInfoDic, "input.txt", "output.png", "detIdsOut.txt")

# with open(outDicTxtFileName, "w") as outfile:
  # for k in pixelCablingInfoDicFed:
    # outfile.write("%s:\n" % (k))
    # for c in pixelCablingInfoDicFed[k]:
      # outfile.write("\t\t%s\n" % (str(pixelCablingInfoDicFed[k][c])))        

pickle.dump(pixelCablingInfoDic, open("DATA/cablingDic.pkl", "wb" ))
for k in pixelCablingInfoDic:
  print(k, pixelCablingInfoDic[k])