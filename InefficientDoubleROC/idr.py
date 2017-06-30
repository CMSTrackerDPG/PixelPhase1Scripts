#!/usr/bin/env python

import sys
import math
from ROOT import *
from copy import deepcopy
from scipy import signal

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
              continue  # do not care about FPIX
              # layer = ((newName.split("_D"))[1])[0]
              # if newName.startswith("FPix_Bm"):
                # layer = "-" + layer
              # layer = "F" + layer
            
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
    self.rocsInRow = 8
    self.rocsInCol = 2
    
    self.thresholdDic = {"B1" : 1000, "B2" : 800, "B3" : 700, "B4" : 700}
    
    self.inputFile = TFile(self.inputFileName)
    self.dicOfModuleHistograms = {}
    
    self.noisyPixelThreshold = 0.25
    
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
        if layer not in self.thresholdDic:
          continue
        
        outputFile.write("-> " + layer + "\n\n")
        k = 0
        for hist in self.dicOfModuleHistograms[layer]:
          print([hist.GetName(), k])
          k = k + 1
          for rocNum in range(self.rocsInRow):
            startPixel = rocNum * self.rocMaxCol + 2
            endPixel = (rocNum + 1) * self.rocMaxCol # - 1 ???
            pixelArr = []
            
            # 1. PASS
            for x in range(startPixel, endPixel):
              pixelArr.append(hist.GetBinContent(x))  
              
            if len(pixelArr) == 0:
              continue                                                # ROC down
              
            medFiltRes = signal.medfilt(pixelArr, 5) # 5 is obligatory to filter doublets!!!
            
            meanOfPixels = sum(medFiltRes) / len(medFiltRes)
            maxMed = max(medFiltRes)
            minMed = min(medFiltRes)          
            # print( meanOfPixels, maxMed, minMed )
            
            # TODO: have to compare each bin value of 2 adjacent bins (making sure that also next one is not also lower than average)
            # one hardcoded threshold does not work either (relative nor absolute)
            
            for x in range(startPixel, endPixel, 2):
              bin1valDiff = minMed - hist.GetBinContent(x+1)
              bin2valDiff = minMed - hist.GetBinContent(x+2)
              # WE ONLY WANT A SET OF TWO COLUMNS
              bin0valDiff = minMed - hist.GetBinContent(x+0) 
              bin3valDiff = minMed - hist.GetBinContent(x+3) 
              
              currentDoubleBinThreshold = minMed / math.sqrt(meanOfPixels) # error in bin entry grows as sqrt(N)
              
              # if bin1valDiff > self.thresholdDic[layer] and bin2valDiff > self.thresholdDic[layer] and not bin3valDiff > self.thresholdDic[layer]:
              if bin1valDiff > currentDoubleBinThreshold  and bin2valDiff > currentDoubleBinThreshold and not bin3valDiff > currentDoubleBinThreshold and not bin0valDiff > currentDoubleBinThreshold:

                rocCol = rocNum + 1
                doubleColInRoc = ((x) % (self.rocMaxCol)) / 2 + 1
                i = i + 1
                
                outputFile.write("%s,\tX: %d\tROC COLUMN: %d\tDOUBLE COL IN ROC: %d\tMIN IN ROC: %f\n" % (hist.GetName(), x, rocCol, doubleColInRoc, minMed))
              
              elif bin1valDiff < -self.noisyPixelThreshold * minMed:
                outputFile.write("NOISY PIXEL %s\n" % (hist.GetName()))
                
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