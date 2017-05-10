#!/usr/bin/env python

import sys
from ROOT import *
from copy import deepcopy

gROOT.SetBatch()        # don't pop up canvases

class HotPixelsReader:
  
  ############################################################################
  
  def __TraverseDirTree(self, dir):
  
    for obj in dir.GetListOfKeys():
      if not obj.IsFolder():
        if obj.ReadObjectAny(TClass.GetClass("TH2")):
          th2 = deepcopy(obj.ReadObj())
          name = th2.GetName()
          if name.startswith(self.lookForStr): #take only module lvl plots
            # print(''.join([dir.GetPath(), '/', name]))
            newName = name.split(self.lookForStr)[1]
            th2.SetName(newName)
            
            # used to sort outputs by disk/layer
            layer = 0
            if newName.startswith("B"):
              layer = "B" + ((newName.split("_LYR"))[1])[0]
            else:
              layer = ((newName.split("_D"))[1])[0]
              if newName.startswith("FPix_Bm"):
                layer = "-" + layer
              layer = "F" + layer
            
            if layer in self.dicOfModuleHistograms:
              self.dicOfModuleHistograms[layer].append(th2)
            else:
              self.dicOfModuleHistograms.update({layer : [th2]})
            
      else:
        self.__TraverseDirTree(obj.ReadObj()) 
        
  ############################################################################
  
  def __init__(self, inputDQMName, outputFileName, dirs):
  
    self.inputFileName = inputDQMName
    self.outputFileName = outputFileName
    self.dirs = dirs
    
    self.lookForStr = "digi_occupancy_per_col_per_row_"
    self.hotPixelThreshold = 4
    self.rocMaxCol = 52
    self.rocMaxRow = 80
    self.rocsInRow = 8
    self.rocsInCol = 2
    
    self.inputFile = TFile(self.inputFileName)
    self.dicOfModuleHistograms = {}
    
    if self.inputFile.IsOpen():
      print("%s opened successfully!" % (self.inputFileName))
      #Get all neeeded histograms
      for dir in self.dirs:
        self.__TraverseDirTree(self.inputFile.Get(dir))
      # print("Histograms to read: %d" % (len(self.dicOfModuleHistograms)))
      
      self.detDict = {}
      
    else:
      print("Unable to open file %s" % (self.inputFileName))
      
  def ReadHistograms(self):
    i = 0
    with open(self.outputFileName, "w") as outputFile:
    
      for layer in self.dicOfModuleHistograms:
        outputFile.write("-> " + layer + "\n\n")
        
        for hist in self.dicOfModuleHistograms[layer]:
          for x in range(self.rocMaxCol * self.rocsInRow):
            for y in range(self.rocMaxRow * self.rocsInCol):
              val = hist.GetBinContent(x + 1, y + 1)
              if val >= self.hotPixelThreshold:
                
                tempXROC = (x / self.rocMaxCol) # 0,...,7
                tempYROC = (y / self.rocMaxRow) # 0, 1
                
                tempXCoordInROC = x % self.rocMaxCol
                tempYCoordInROC = y % self.rocMaxRow
                
                realXROC, realYROC = tempXROC, tempYROC
                xCoordInROC, yCoordInROC = tempXCoordInROC, tempYCoordInROC
                
                rocNum = 0
                
                if hist.GetName().find("BPix_Bp") != -1: #zero ROC is in top left corner
                  realYROC = 1 - tempYROC
                  if realYROC == 1:
                    rocNum = 15 - realXROC
                    xCoordInROC = self.rocMaxCol - 1 - xCoordInROC
                  else:
                    rocNum = realXROC
                    yCoordInROC = self.rocMaxRow - 1 - yCoordInROC
                else: # zero ROC is in bottom right corner
                  realXROC = 7 - tempXROC
                  if realYROC == 1:
                    rocNum = 15 - realXROC
                    yCoordInROC = self.rocMaxRow - 1 - yCoordInROC
                  else:
                    rocNum = realXROC
                    xCoordInROC = self.rocMaxCol - 1 - xCoordInROC
                    
                outputFile.write("%s, [modCoord: (%d, %d); roc=%d rocCoord: (%d, %d)] : %d\n"%(hist.GetName(), x, y, rocNum, xCoordInROC, yCoordInROC, val))
                
                # return
                i = i + 1
                
        outputFile.write("\n")        
    print("Number of hot pixels: %d"%(i))
      
      
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--


for i in range(1, len(sys.argv), 1):
  if i == 1:
    inputFileName = sys.argv[i]

runNum = ((inputFileName.split("."))[0].split("_R000"))[1]
print("Run number: %s"%(runNum))
baseRootDir = ["DQMData/Run " + runNum + "/PixelPhase1/Run summary/Phase1_MechanicalView"]
print(baseRootDir[0])
outputFileName = "hotpixels_" + runNum + ".out"

readerObj = HotPixelsReader(inputFileName, outputFileName, baseRootDir)  
readerObj.ReadHistograms()