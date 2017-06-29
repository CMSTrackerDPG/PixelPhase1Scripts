#!/usr/bin/env python

import sys
from ROOT import *
from copy import deepcopy

gROOT.SetBatch()        # don't pop up canvases

class InefficientDeadROCs:
  ############################################################################
  
  def __TraverseDirTree(self, dir):
  
    for obj in dir.GetListOfKeys():
      if not obj.IsFolder():
        if obj.ReadObjectAny(TClass.GetClass("TH1")):
          th1 = deepcopy(obj.ReadObj())
          name = th1.GetName()
          if name.startswith(self.lookForStr) and not name.startswith(self.lookForStr + "per"): #take only module lvl plots
            # print(''.join([dir.GetPath(), '/', name]))
            newName = name.split(self.lookForStr)[1]
            th1.SetName(newName)
            
            # used to sort outputs by disk/layer
            layer = 0
            # print(newName)
            if newName.startswith("B"):
              layer = "B" + ((newName.split("_LYR"))[1])[0]
            else:
              layer = ((newName.split("_D"))[1])[0]
              if newName.startswith("FPix_Bm"):
                layer = "-" + layer
              layer = "F" + layer
            
            if layer in self.dicOfModuleHistograms:
              self.dicOfModuleHistograms[layer].append(th1)
            else:
              self.dicOfModuleHistograms.update({layer : [th1]})        
              
            # break; # for speed...
      else:
        self.__TraverseDirTree(obj.ReadObj())
        
  def __init__(self, inputDQMName, outputFileName, dirs):
  
    self.inputFileName = inputDQMName
    self.outputFileName = outputFileName
    self.dirs = dirs
    
    self.lookForStr = "digi_occupancy_per_col_"
    
    # self.hotPixelThreshold = 4
    self.rocMaxCol = 52
    self.rocMaxRow = 80
    self.relativeDiffTh = 0.3 # TO TUNE
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
        
          recentDoubleBin = [-1, -1, 0] # pattern recognition window
          
          for rocNum in range(self.rocsInRow):
            startPixel = rocNum * self.rocMaxCol + 2
            endPixel = (rocNum + 1) * self.rocMaxCol # - 1 ???
            pixelArr = []
            for x in range(startPixel, endPixel):
              pixelArr.append(hist.GetBinContent(x))
              
            meanOfPixels = sum(pixelArr) / len(pixelArr)
            
            for x in range(startPixel, endPixel, 2):
              currMean = (hist.GetBinContent(x+1) + hist.GetBinContent(x+2)) * 0.5
              
              if currMean < 0.9 * meanOfPixels:
              
                rocCol = rocNum + 1
                doubleColInRoc = ((x) % (self.rocMaxCol)) / 2 + 1
                i = i + 1
                
                outputFile.write("%s,\tX: %d\tROC COLUMN: %d\tDOUBLE COL IN ROC: %d\n" % (hist.GetName(), x, rocCol, doubleColInRoc))
                
        
          # for x in range(0, self.rocMaxCol * self.rocsInRow, 2):
            # val = hist.GetBinContent(x + 1) + hist.GetBinContent(x + 2)
              
            # recentDoubleBin[2] = val
            
            # # print(x, val, recentDoubleBin)
            
            # # exlude init and div by 0
            # if not -1 in recentDoubleBin and recentDoubleBin[0] != 0 and recentDoubleBin[2] != 0:
              # relDeltaLeft = (recentDoubleBin[1] - recentDoubleBin[0]) #/ recentDoubleBin[0]
              # relDeltaRight =(recentDoubleBin[1] - recentDoubleBin[2]) #/ recentDoubleBin[2]
              
              # if relDeltaLeft < 0 and abs(relDeltaLeft) > 800: #self.relativeDiffTh:
                # if relDeltaRight < 0 and abs(relDeltaRight) > 800: #self.relativeDiffTh:
                
                  # rocCol = ((x + 1) // (self.rocMaxCol)) + 1
                  # doubleColInRoc = ((x) % (self.rocMaxCol)) / 2 + 1
                
                  # i = i + 1
                  # print("x: " + str(x) + "\trocCol: " + str(rocCol) + "\tdoubleColInRoc: " + str(doubleColInRoc) + "\nFound sequence " + str(recentDoubleBin) + " in " + hist.GetName())
                  # outputFile.write("%s,\tX: %d\tROC COLUMN: %d\tDOUBLE COL IN ROC: %d\n" % (hist.GetName(), x, rocCol, doubleColInRoc))
            
            # # SHIFT VALUES
            # recentDoubleBin[0] = recentDoubleBin[1]
            # recentDoubleBin[1] = recentDoubleBin[2]
              
              # if val >= self.hotPixelThreshold:
                
                # tempXROC = (x / self.rocMaxCol) # 0,...,7
                # tempYROC = (y / self.rocMaxRow) # 0, 1
                
                # tempXCoordInROC = x % self.rocMaxCol
                # tempYCoordInROC = y % self.rocMaxRow
                
                # realXROC, realYROC = tempXROC, tempYROC
                # xCoordInROC, yCoordInROC = tempXCoordInROC, tempYCoordInROC
                
                # rocNum = 0
                
                # if hist.GetName().find("BPix_Bp") != -1: #zero ROC is in top left corner
                  # realYROC = 1 - tempYROC
                  # if realYROC == 1:
                    # rocNum = 15 - realXROC
                    # xCoordInROC = self.rocMaxCol - 1 - xCoordInROC
                  # else:
                    # rocNum = realXROC
                    # yCoordInROC = self.rocMaxRow - 1 - yCoordInROC
                # else: # zero ROC is in bottom right corner
                  # realXROC = 7 - tempXROC
                  # if realYROC == 1:
                    # rocNum = 15 - realXROC
                    # yCoordInROC = self.rocMaxRow - 1 - yCoordInROC
                  # else:
                    # rocNum = realXROC
                    # xCoordInROC = self.rocMaxCol - 1 - xCoordInROC
                    
                # outputFile.write("%s, [modCoord: (%d, %d); roc=%d rocCoord: (%d, %d)] : %d\n"%(hist.GetName(), x, y, rocNum, xCoordInROC, yCoordInROC, val))
                
                # return
                
                
        outputFile.write("\n")        
    print("Number of inefficient double columns: %d"%(i))
      
      
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--
for i in range(1, len(sys.argv), 1):
  if i == 1:
    inputFileName = sys.argv[i]

runNum = ((inputFileName.split("."))[0].split("_R000"))[1]
print("Run number: %s"%(runNum))
baseRootDir = ["DQMData/Run " + runNum + "/PixelPhase1/Run summary/Phase1_MechanicalView"]
print(baseRootDir[0])
outputFileName = "inefficientDeadROCs_" + runNum + ".out"

readerObj = InefficientDeadROCs(inputFileName, outputFileName, baseRootDir)  
readerObj.ReadHistograms()