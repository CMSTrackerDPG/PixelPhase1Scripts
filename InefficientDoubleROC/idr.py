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
              # continue  # do not care about FPIX
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
        
  def __init__(self, inputDQMName, outputFileName, noiseOutputFileName, dirs):
  
    self.inputFileName = inputDQMName
    self.outputFileName = outputFileName
    self.noiseOutputFileName = noiseOutputFileName
    self.dirs = dirs
    
    self.lookForStr = "digi_occupancy_per_col_"
    
    # self.hotPixelThreshold = 4
    self.rocMaxCol = 52
    self.rocMaxRow = 80
    self.rocsInRow = 8
    self.rocsInCol = 2
    
    self.inputFile = TFile(self.inputFileName)
    self.dicOfModuleHistograms = {}
    
    self.noisyPixelThreshold = 0.1
    
    if self.inputFile.IsOpen():
      print("%s opened successfully!" % (self.inputFileName))
      #Get all neeeded histograms
      for dir in self.dirs:
        self.__TraverseDirTree(self.inputFile.Get(dir))
      # print("Histograms to read: %d" % (len(self.dicOfModuleHistograms)))
      
      self.detDict = {}
      
    else:
      print("Unable to open file %s" % (self.inputFileName))
      
  def __lmsExp(self, data, xMin, xMax):
    meanOfX = (xMax + xMin) * 0.5
    meanOfY = sum( [math.log(data[i]) for i in range(len(data))] ) / len(data)
    
    D = 0
    for i in range(xMin, xMax + 1):
      D = D + (i - meanOfX)**2
      # print(D)

    a = 0
    for i in range(len(data)):
      a = a + math.log(data[i]) * (xMin + i - meanOfX)
    a = a/D
    
    lnb = meanOfY - a * meanOfX
    
    return a, math.exp(lnb)
    
  def __lmsLin(self, data, xMin, xMax):
    meanOfX = (xMax + xMin) * 0.5
    meanOfY = sum(data) / len(data)
    
    D = 0
    for i in range(xMin, xMax + 1):
      D = D + (i - meanOfX)**2
      # print(D)

    a = 0
    for i in range(len(data)):
      a = a + data[i] * (xMin + i - meanOfX)
    a = a/D
    
    b = meanOfY - a * meanOfX
    
    return a, b, D
      
  def ReadHistograms(self):      
    doubleDeadCols = 0
    noisyCols = 0
    
    with open(self.noiseOutputFileName, "w") as noiseFile: 
    
      with open(self.outputFileName, "w") as outputFile:
      
        for layer in self.dicOfModuleHistograms:
          # if layer not in self.thresholdDic:
            # continue
          
          outputFile.write("-> " + layer + "\n\n")
          noiseFile.write("-> " + layer + "\n\n")
          
          k = 0
          for hist in self.dicOfModuleHistograms[layer]:
            print([hist.GetName(), k])
            k = k + 1
            for rocNum in range(self.rocsInRow):
              startPixel = rocNum * self.rocMaxCol + 2
              endPixel = (rocNum + 1) * self.rocMaxCol # - 1 ???
              pixelArr = []
              
              rocCol = rocNum + 1
              
              # 1. PASS
              for x in range(startPixel, endPixel):
                pixelArr.append(hist.GetBinContent(x))  
                
              if len(pixelArr) == 0:
                continue                                                # ROC down
              
              medFiltRes = pixelArr
              for i in range(3):
                medFiltRes = signal.medfilt(medFiltRes, 5) # 5 is obligatory to filter doublets!!!
                
              # now calc LMS coefficents
              
              if "F" not in layer:
                meanOfPixels = sum(medFiltRes) / len(medFiltRes)
                maxMed = max(medFiltRes)
                minMed = min(medFiltRes)          
                # print( meanOfPixels, maxMed, minMed )
                
                # TODO: have to compare each bin value of 2 adjacent bins (making sure that also next one is not also lower than average)
                # one hardcoded threshold does not work either (relative nor absolute)
                
                for x in range(startPixel, endPixel, 1):
                  bin1valDiff = minMed - hist.GetBinContent(x+0)
                  bin2valDiff = minMed - hist.GetBinContent(x+1)
                  # WE ONLY WANT A SET OF TWO COLUMNS SO ADJACENT COLUMNS HAVE TO BE NORMAL
                  bin0valDiff = minMed - hist.GetBinContent(x-1) 
                  bin3valDiff = minMed - hist.GetBinContent(x+2) 
                  
                  currentDoubleBinThreshold = minMed / math.sqrt(meanOfPixels) * 2.5 # error in bin entry grows as sqrt(N)
                                    
                  # if bin1valDiff > self.thresholdDic[layer] and bin2valDiff > self.thresholdDic[layer] and not bin3valDiff > self.thresholdDic[layer]:
                  if bin1valDiff > currentDoubleBinThreshold  and bin2valDiff > currentDoubleBinThreshold and not bin3valDiff > currentDoubleBinThreshold and not bin0valDiff > currentDoubleBinThreshold:

                    doubleColInRoc = ((x) % (self.rocMaxCol)) // 2 + 1
                    doubleDeadCols = doubleDeadCols + 1
                    
                    outputFile.write("%s,\tX: %d-%d\tROC COLUMN: %d\tDOUBLE COL IN ROC: %d\tTH: %f\tMIN IN ROC: %f\tBINVAL: %f\n" % (hist.GetName(), x+0, x+1, rocCol, doubleColInRoc, currentDoubleBinThreshold, minMed, hist.GetBinContent(x+0)))

                  # HANDLE NOISY PIXELS
                  if maxMed - hist.GetBinContent(x) < -self.noisyPixelThreshold * maxMed:
                    colInRoc = (x) % (self.rocMaxCol) + 1
                    
                    noisyCols = noisyCols + 1
                    
                    noiseFile.write("%s,\tX: %d\tROC COLUMN: %d\tCOL IN ROC: %d\tMEAN IN ROC: %f\tVAL: %f\n" % (hist.GetName(), x, rocCol, colInRoc, meanOfPixels, hist.GetBinContent(x)))
              else:
                useLin = True
                # <D> might be used for high noise ROC recognition
                a, b, D = self.__lmsLin(medFiltRes, startPixel, endPixel)
                
                # if 0 in medFiltRes:
                  # useLin = True
                  # a, b = self.__lmsLin(medFiltRes, startPixel, endPixel)
                # else:
                  # a, b = self.__lmsExp(medFiltRes, startPixel, endPixel)
                  # if b > 1000000:  # it becomes more and more linear
                    # useLin = True
                    # a, b = self.__lmsLin(medFiltRes, startPixel, endPixel)
                              
                meanOfPixels = sum(medFiltRes) / len(medFiltRes)
                
                # print("a: %f\tb: %f" % (a, b))
                
                for x in range(startPixel, endPixel, 1):
                  
                  if useLin == True:
                    linVal1 = a * (x + 0) + b
                    linVal2 = a * (x + 1) + b
                    
                    linVal0 = a * (x - 1) + b
                    linVal3 = a * (x + 2) + b
                  else:
                    linVal1 = b * math.exp(a * (x + 0))
                    linVal2 = b * math.exp(a * (x + 1))
                                           
                    linVal0 = b * math.exp(a * (x - 1))
                    linVal3 = b * math.exp(a * (x + 2))
                  
                  bin1valDiff = linVal1 - hist.GetBinContent(x+0)
                  bin2valDiff = linVal2 - hist.GetBinContent(x+1)
                  # WE ONLY WANT A SET OF TWO COLUMNS SO ADJACENT COLUMNS HAVE TO BE NORMAL
                  bin0valDiff = linVal0 - hist.GetBinContent(x-1) 
                  bin3valDiff = linVal3 - hist.GetBinContent(x+2) 
                  
                  # print(linVal1, linVal2, linVal1 + linVal2, (linVal1 + linVal2) * 0.5)
                  currentDoubleBinThreshold = math.sqrt((linVal1 + linVal2) * 0.5) * 8
                  
                  # if bin1valDiff > self.thresholdDic[layer] and bin2valDiff > self.thresholdDic[layer] and not bin3valDiff > self.thresholdDic[layer]:
                  if bin1valDiff > currentDoubleBinThreshold  and bin2valDiff > currentDoubleBinThreshold and not bin3valDiff > currentDoubleBinThreshold and not bin0valDiff > currentDoubleBinThreshold:

                    doubleColInRoc = ((x) % (self.rocMaxCol)) // 2 + 1
                    doubleDeadCols = doubleDeadCols + 1
                    
                    outputFile.write("%s,\tX: %d-%d\tROC COLUMN: %d\tDOUBLE COL IN ROC: %d\tTH: %f\tLINVAL: %f\tBINVAL: %f\n" % (hist.GetName(), x+0, x+1, rocCol, doubleColInRoc, currentDoubleBinThreshold, linVal1, hist.GetBinContent(x+0)))

                  # HANDLE NOISY PIXELS
                  if hist.GetBinContent(x) > 1.2 * linVal1:
                    colInRoc = (x) % (self.rocMaxCol) + 1
                    
                    noisyCols = noisyCols + 1
                    
                    noiseFile.write("%s,\tX: %d\tROC COLUMN: %d\tCOL IN ROC: %d\tMEAN IN ROC: %f\tVAL: %f\tLINVAL: %f\n" % (hist.GetName(), x, rocCol, colInRoc, meanOfPixels, hist.GetBinContent(x), linVal1))
                
                  
          outputFile.write("\n")    
          noiseFile.write("\n")
    print("Number of inefficient double columns: %d"%(doubleDeadCols))
    print("Number of noisy cols: %d"%(noisyCols))
      
      
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--
for i in range(1, len(sys.argv), 1):
  if i == 1:
    inputFileName = sys.argv[i]

runNum = ((inputFileName.split("."))[0].split("_R000"))[1]
print("Run number: %s"%(runNum))
baseRootDir = ["DQMData/Run " + runNum + "/PixelPhase1/Run summary/Phase1_MechanicalView"]
print(baseRootDir[0])
outputFileName = "inefficientDROCs_" + runNum + ".out"
noiseOutputFileName = "noisyROCs_" + runNum + ".out"

readerObj = InefficientDeadROCs(inputFileName, outputFileName, noiseOutputFileName, baseRootDir)  
readerObj.ReadHistograms()