#!/usr/bin/env python

import sys
from ROOT import *
from copy import deepcopy
from config import *
import os

gROOT.SetBatch()        # don't pop up canvases
gStyle.SetOptStat()
gStyle.SetPalette(1) #palette change

###################################################################

gEnv.SetValue("Davix.GSI.UserCert", pathToGlobus + userCertInGlobus)
gEnv.SetValue("Davix.GSI.UserKey", pathToGlobus + userKeyInGlobus)

gEnv.SetValue("Davix.Debug", "1")

# gEnv.Print()

runNumber = 305810

###################################################################

class NoisyROCsReader:
  
  ############################################################################
  
  def __TraverseDirTree(self, dir):
  
    for obj in dir.GetListOfKeys():
      if not obj.IsFolder():
        if obj.ReadObjectAny(TClass.GetClass("TH2")):
          th2 = deepcopy(obj.ReadObj())
          name = th2.GetName()
          if name.startswith(self.lookForStr): #take only module lvl plots
            # print(''.join([dir.GetPath(), '/', name]))
            
            histogramPath = '/'.join(["PixelPhase1", '/'.join(dir.GetPath().split("/")[5:]), name])
            # print(histogramPath)
            
            newName = name.split(self.lookForStr)[1]
            # print(newName)
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
              self.dicOfModuleHistograms[layer].append([th2, histogramPath])
            else:
              self.dicOfModuleHistograms.update({layer : [[th2, histogramPath]]})
            
      else:
        self.__TraverseDirTree(obj.ReadObj()) 
        
  def __AnalyzeROC(self, xStart, yStart, hist):
    accum = 0
    for x in range(self.rocMaxCol):
      for y in range(self.rocMaxRow):
        # print((xStart + x + 1, yStart + y + 1))
        val = hist.GetBinContent(xStart + x + 1, yStart + y + 1)
        
        accum = accum + val
        
        if accum >= self.ROCThreshold:
          return accum
          
    return accum
    
  def __BuildLink(self, histPath):  
    pos = histPath.rfind("/")
    
    rootPath = histPath[0 : pos]
    # print(rootPath)
    linkArray = ["https://cmsweb.cern.ch/dqm/online/start?runnr=" + str(self.runNum),
                "dataset=/Global/Online/ALL",
                "sampletype=online_data",
                "filter=all",
                "referencepos=overlay",
                "referenceshow=customise",
                "referencenorm=True",
                "referenceobj1=refobj",
                "referenceobj2=none",
                "referenceobj3=none",
                "referenceobj4=none",
                "search=",
                "striptype=object",
                "stripruns=",
                "stripaxis=run",
                "stripomit=none",
                "workspace=PixelPhase1",
                "size=M",
                "root=" + rootPath,
                "focus=" + histPath,
                "zoom=yes"
                ]
                
    theLink = ';'.join(linkArray)
    # print(theLink)
    return theLink
             
  ############################################################################
  
  def __init__(self, runNum, inputDQMName, outputDir, outputFileName, dirs):
  
    self.runNum = runNum
    self.inputFileName = inputDQMName
    self.outputDir = outputDir
    self.outputFileName = self.outputDir + "/" + outputFileName
    self.dirs = dirs
    
    self.lookForStr = "digi_occupancy_per_col_per_row_"
    self.ROCThreshold = 1000
    self.plotThreshold = plotThreshold
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
      
  def AnalyzeHistograms(self):
  
    if not os.path.exists(self.outputDir):
      os.system("mkdir " + self.outputDir)
    
    with open(self.outputFileName, "w") as outputFile:
      
      outputFile.write("<html><head></head><body>")
      outputFile.write("<span style=\"font-size: large; font-weight: bold;\"> Noisy cosmic ROCs for the run: " + str(self.runNum) + "</br></span>")
      for layer in self.dicOfModuleHistograms:
        outputFile.write("</br> -> " + layer + "</br>")
        outputFile.write("<table style=\"width: 700px;\">")
        
        # currentDir = self.outputDir + "/" + layer
        # if not os.path.exists(currentDir):
          # os.system("mkdir " + currentDir)
        
        for histObj in self.dicOfModuleHistograms[layer]:
          hist = histObj[0]
          histPath = histObj[1]
          
          maxVal = hist.GetMaximum()
          if maxVal >= self.plotThreshold:
            linkPath = self.__BuildLink(histPath)
            
            outputFile.write("<tr><td style=\"width: 500px;\">" + hist.GetName() + "</td><td style=\"width: 200px;\"><a href=\"" + linkPath + "\"> See plot</a></td></tr>")
            
        outputFile.write("</table>")
            
      outputFile.write("</body></html>")
            
          # for rx in range(self.rocsInRow):
            # for ry in range(self.rocsInCol):
              # xStart = rx * self.rocMaxCol
              # yStart = ry * self.rocMaxRow
              
              # ROCOccupancy = self.__AnalyzeROC(xStart, yStart, hist)
              # if ROCOccupancy >= self.ROCThreshold:
                # realXROC, realYROC = rx, ry
                
                # rocNum = 0
                
                # theName = hist.GetName()
                # if theName.find("BPix_Bp") != -1: #zero ROC is in top left corner
                  # realYROC = 1 - realYROC
                  # if realYROC == 1:
                    # rocNum = 15 - realXROC                    
                  # else:
                    # rocNum = realXROC
                # else: # zero ROC is in bottom right corner
                  # realXROC = 7 - realXROC
                  # if realYROC == 1:
                    # rocNum = 15 - realXROC
                  # else:
                    # rocNum = realXROC
                    
                # c = TCanvas(theName, theName, canvasWidth, canvasHeight)
                # hist.Draw("COLZ")
                # hist.SetStats(0)
                # c.Print(currentDir + "/" + theName + ".png")
                
                    
                # # print("%s roc=%d, rx=%d ry=%d" % (hist.GetName(), rocNum, rx, ry))
                # outputFile.write("%s roc=%d\n" % (hist.GetName(), rocNum))
              
  
###################################################################

for i in range(1, len(sys.argv)):
  if i == 1:
    runNumber = int(sys.argv[1])

runNumberStr = str(runNumber)

runStrHigh = "000" + runNumberStr[0:2] + "x" * 4
runStrMedium = "000" + runNumberStr[0:4] + "x" * 2

wholePathToTheRemoteFile = httpsMainDir + runStrHigh + "/" + runStrMedium + "/DQM_V0001_PixelPhase1_R000" + runNumberStr + ".root"

print("Looking for:\n\t" + wholePathToTheRemoteFile)
g = TFile.Open(wholePathToTheRemoteFile)

if g and g.IsOpen():
  print("Remote file successfully open!")
  print("Creating local copy...")
  g.Cp(tmpFileName)
  g.Close()
else:
  print("Failed to load the file!")
  
baseRootDir = ["DQMData/Run " + runNumberStr + "/PixelPhase1/Run summary/Phase1_MechanicalView"]
print(baseRootDir[0])
outputFileName = "noisyCosmic_" + runNumberStr + "_report.html"

readerObj = NoisyROCsReader(runNumber, tmpFileName, outputDir, outputFileName, baseRootDir)
readerObj.AnalyzeHistograms()
  
