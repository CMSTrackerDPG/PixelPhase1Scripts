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
        if obj.ReadObjectAny(TClass.GetClass("TH2")):
          th1 = deepcopy(obj.ReadObj())
          name = th1.GetName()
          if name.startswith(self.lookForStr): #take only module lvl plots
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
      else:
        self.__TraverseDirTree(obj.ReadObj())
        
  def __init__(self, inputDQMName, outputFileName, noiseOutputFileName, dirs):
  
    self.inputFileName = inputDQMName
    self.outputFileName = outputFileName
    self.noiseOutputFileName = noiseOutputFileName
    self.dirs = dirs
    
    self.lookForStr = "digi_occupancy_per_col_per_row_"
    
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
    
  def __getROCData(self, hist, startPixel, endPixel, row, repeatFilter = 3, filterKernelSize = 5):
    pixelArr = []
    for x in range(startPixel, endPixel):
      columnSum = 0
      for y in range(row * self.rocMaxRow, (row + 1) * self.rocMaxRow):
        columnSum = columnSum + hist.GetBinContent(x, y + 1) # bins numeration starts from 1
      pixelArr.append(columnSum)  
      
    if len(pixelArr) == 0:
      return None, None                                             # ROC down
    
    medFiltRes = pixelArr
    for i in range(repeatFilter):
      medFiltRes = signal.medfilt(medFiltRes, filterKernelSize) # 5 is obligatory to filter doublets!!!
      
    return pixelArr, medFiltRes
    
    
  def __determineBarrelNoise(self, noiseFile, histName, meanOfPixels, maxMed, val, pos, rocCol, rocRow):
    if meanOfPixels < 200:
      print("Very low mean occupancy: %f in ROC %s:COL%dxROC%d\nSkipping noisy ROC calculation" % (meanOfPixels, histName, rocCol, rocRow) )
      
    elif val > 1.5 * maxMed:
      colInRoc = (pos) % (self.rocMaxCol) + 1      
      noiseFile.write("%s,\tX: %d\tROC COLUMN: %d\tROC ROW: %d\tCOL IN ROC: %d\tMEAN IN ROC: %f\tVAL: %f\n" % (histName, pos, rocCol, rocRow, colInRoc, meanOfPixels, val))
      
      return 1
    return 0
    
  def __determineEndcapNoise(self, noiseFile, histName, meanOfPixels, linVal, val, pos, rocCol, rocRow):
    if meanOfPixels < 200:
      print("Very low mean occupancy: %f in ROC %s:\tCOL%dxROC%d\nSkipping noisy ROC calculation" % (meanOfPixels, histName, rocCol, rocRow) )
    
    elif val > 1.5 * linVal:
      colInRoc = (pos) % (self.rocMaxCol) + 1  
      noiseFile.write("%s,\tX: %d\tROC COLUMN: %d\tROC ROW: %d\tCOL IN ROC: %d\tMEAN IN ROC: %f\tVAL: %f\tLINVAL: %f\n" % (histName, pos, rocCol, rocRow, colInRoc, meanOfPixels, val, linVal))
        
      return 1
    return 0
    
  def __determineBarrelDColInefficiencyAndNoise(self, medFiltRes, histName, pixelArr, startPixel, rocCol, rocRow, outputFile, noiseFile):
    meanOfPixels = sum(medFiltRes) / len(medFiltRes)
    maxMed = max(medFiltRes)
    minMed = min(medFiltRes)          
    # print( meanOfPixels, maxMed, minMed )
    
    doubleDeadCols = 0
    noisyCols = 0
    
    # for x in range(startPixel, endPixel, 1):
    for i in range(1, len(pixelArr) - 2):
      bin1valDiff = minMed - pixelArr[i + 0]#hist.GetBinContent(x+0)
      bin2valDiff = minMed - pixelArr[i + 1]
      # WE ONLY WANT A SET OF TWO COLUMNS SO ADJACENT COLUMNS HAVE TO BE NORMAL
      bin0valDiff = minMed - pixelArr[i - 1]
      bin3valDiff = minMed - pixelArr[i + 2]
      
      currentDoubleBinThreshold = minMed / math.sqrt(meanOfPixels) * 2.5 # error in bin entry grows as sqrt(N)
                        
      if bin1valDiff > currentDoubleBinThreshold and bin2valDiff > currentDoubleBinThreshold and not bin3valDiff > currentDoubleBinThreshold and not bin0valDiff > currentDoubleBinThreshold:

        doubleColInRoc = ((i + startPixel) % (self.rocMaxCol)) // 2 + 1
        doubleDeadCols = doubleDeadCols + 1
        
        outputFile.write("%s,\tX: %d-%d\tROC COLUMN: %d\tROC ROW: %d\tDOUBLE COL IN ROC: %d\tTH: %f\tMIN IN ROC: %f\tBINVAL: %f\n" % (histName, startPixel + (i + 0), startPixel + (i + 1), rocCol, rocRow, doubleColInRoc, currentDoubleBinThreshold, minMed, pixelArr[i]))

      # HANDLE NOISY PIXELS
      noisyCols = noisyCols + self.__determineBarrelNoise(noiseFile, histName, meanOfPixels, maxMed, pixelArr[i], startPixel + i, rocCol, rocRow)
      if i == len(pixelArr) - 3: #  CHECK NOISYNESS IN THE RIGHTMOST INNER COL
        noisyCols = noisyCols + self.__determineBarrelNoise(noiseFile, histName, meanOfPixels, maxMed, pixelArr[i + 1], startPixel + i + 1, rocCol, rocRow)
        
    return doubleDeadCols, noisyCols
  
  def __determineEndcapDColInefficiencyAndNoise(self, medFiltRes, histName, pixelArr, startPixel, rocCol, rocRow, outputFile, noiseFile):
    doubleDeadCols = 0
    noisyCols = 0
    
    useLin = True
    # <D> might be used for high noise ROC recognition
    a, b, D = self.__lmsLin(medFiltRes, startPixel, len(medFiltRes) + startPixel)
                  
    meanOfPixels = sum(medFiltRes) / len(medFiltRes)
    
    # for x in range(startPixel, endPixel, 1):
    for i in range(1, len(pixelArr) - 2):
      
      if useLin == True:
        linVal1 = a * (i + startPixel + 0) + b
        linVal2 = a * (i + startPixel + 1) + b
        
        linVal0 = a * (i + startPixel - 1) + b
        linVal3 = a * (i + startPixel + 2) + b
      else:
        linVal1 = b * math.exp(a * (i + startPixel + 0))
        linVal2 = b * math.exp(a * (i + startPixel + 1))
                               
        linVal0 = b * math.exp(a * (i + startPixel - 1))
        linVal3 = b * math.exp(a * (i + startPixel + 2))
      
      bin1valDiff = linVal1 - pixelArr[i + 0]
      bin2valDiff = linVal2 - pixelArr[i + 1]
      # WE ONLY WANT A SET OF TWO COLUMNS SO ADJACENT COLUMNS HAVE TO BE NORMAL
      bin0valDiff = linVal0 - pixelArr[i - 1]
      bin3valDiff = linVal3 - pixelArr[i + 2] 
         
      try:
        currentDoubleBinThreshold = math.sqrt((linVal1 + linVal2) * 0.5) * 8
      except:
        print(a, b, startPixel, i, linVal1, linVal2)
        continue
      
      if bin1valDiff > currentDoubleBinThreshold and bin2valDiff > currentDoubleBinThreshold and not bin3valDiff > currentDoubleBinThreshold and not bin0valDiff > currentDoubleBinThreshold:

        doubleColInRoc = ((i + startPixel) % (self.rocMaxCol)) // 2 + 1
        doubleDeadCols = doubleDeadCols + 1
        
        outputFile.write("%s,\tX: %d-%d\tROC COLUMN: %d\tROC ROW: %d\tDOUBLE COL IN ROC: %d\tTH: %f\tLINVAL: %f\tBINVAL: %f\n" % (histName, startPixel + (i + 0), startPixel + (i + 1), rocCol, rocRow, doubleColInRoc, currentDoubleBinThreshold, linVal1, pixelArr[i]))

      # HANDLE NOISY PIXELS
      noisyCols = noisyCols + self.__determineEndcapNoise(noiseFile, histName, meanOfPixels, linVal1, pixelArr[i], i + startPixel, rocCol, rocRow)
      if i == len(pixelArr) - 3: #  CHECK NOISYNESS IN THE RIGHTMOST INNER COL
        noisyCols = noisyCols + self.__determineEndcapNoise(noiseFile, histName, meanOfPixels, linVal2, pixelArr[i + 1], i + 1 + startPixel, rocCol, rocRow)
    
    return doubleDeadCols, noisyCols
      
  def ReadHistograms(self):      
    doubleDeadCols = 0
    noisyCols = 0
    
    with open(self.noiseOutputFileName, "w") as noiseFile: 
    
      with open(self.outputFileName, "w") as outputFile:
      
        for layer in self.dicOfModuleHistograms:
          
          outputFile.write("-> " + layer + "\n\n")
          noiseFile.write("-> " + layer + "\n\n")
          
          # if "F" in layer:
            # continue
          
          for hist in self.dicOfModuleHistograms[layer]:          
            for row in range(2):          
              for rocNum in range(self.rocsInRow):
                startPixel = rocNum * self.rocMaxCol + 1
                endPixel = (rocNum + 1) * self.rocMaxCol + 1 # - 1 ???
                
                rocCol = rocNum + 1
                
                pixelArr, medFiltRes = self.__getROCData(hist, startPixel, endPixel, row)
                if pixelArr == None:
                  continue
                
                # print(len(pixelArr))
                
                if "F" not in layer:
                  result = self.__determineBarrelDColInefficiencyAndNoise(medFiltRes, hist.GetName(), pixelArr, startPixel, rocCol, row + 1, outputFile, noiseFile)
                else:
                  result = self.__determineEndcapDColInefficiencyAndNoise(medFiltRes, hist.GetName(), pixelArr, startPixel, rocCol, row + 1, outputFile, noiseFile)
                  
                doubleDeadCols = doubleDeadCols + result[0]
                noisyCols = noisyCols + result[1]                
                  
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