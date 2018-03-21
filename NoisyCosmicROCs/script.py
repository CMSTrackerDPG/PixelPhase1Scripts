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
            histogramPath = histogramPath.replace("+", "%2B")
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
    
  def __DetermineCluster(self, hist, value):
    binNumX = hist.FindLastBinAbove(value - 1, 1)
    binNumY = hist.FindLastBinAbove(value - 1, 2)
    
    crawlPattern = [ [-1, 1],  [0, 1],  [1, 1],
                     [-1, 0],  [0, 0],  [1, 0],
                     [-1, -1], [0, -1], [1, -1]]
    
    pixelsInNoiseCluster = 0
    for i in range(len(crawlPattern)):

      val = hist.GetBinContent(binNumX + crawlPattern[i][0],
                               binNumY + crawlPattern[i][1])
      #print binNumX + crawlPattern[i][0]
      #print binNumY + crawlPattern[i][1]                        
      if (pixelsInNoiseCluster==0 and  val >= clusterThreshold) or (pixelsInNoiseCluster!=0 and  val >= 0.6*clusterThreshold): 
        pixelsInNoiseCluster = pixelsInNoiseCluster + 1
    
    return True if pixelsInNoiseCluster >= self.pixelsInClusterThreshold else False
    
  def __DetermineScatteredCluster(self, hist, value):
    binNumX = hist.FindLastBinAbove(value - 1, 1)
    binNumY = hist.FindLastBinAbove(value - 1, 2)
    
    area = (2.0 * self.scatteredClusterRadius + 1) * (2.0 * self.scatteredClusterRadius + 1) #- 1 # -1 is to exclude the central bin
    
    pixelsInNoiseCluster = 1
    for i in range(-self.scatteredClusterRadius, self.scatteredClusterRadius + 1, 1):
      for j in range(-self.scatteredClusterRadius, self.scatteredClusterRadius + 1, 1):
        
       # if i == j and i == 0: 
       #   continue
      
        currX = binNumX + i
        currY = binNumY + j
        
        if currX < 1 or currX > self.rocMaxCol * self.rocsInRow or currY < 1 or currY > self.rocMaxRow * self.rocsInCol:
          area = area - 1
          continue
          
        val = hist.GetBinContent(currX, currY)
        
        if val >= scatteredClusterThreshold:
          pixelsInNoiseCluster = pixelsInNoiseCluster + 1
      
    fraction = pixelsInNoiseCluster
    
    return True if fraction >= self.scatteredClusterNumberThreshold else False
    
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
  
  def __init__(self, runNum, inputDQMName, outputDir, dirs):
  
    self.runNum                         = runNum
    self.inputFileName                  = inputDQMName
    self.outputDir                      = outputDir
    
    self.outputFileNames = [self.outputDir + "/" + str(runNum) + "/noisyPixels_report.html",
                            self.outputDir + "/" + str(runNum) + "/noisyPixels_Clustered_report.html",
                            self.outputDir + "/" + str(runNum) + "/noisyPixels_Spray_report.html"]
    
    # self.outputFileName                 = self.outputDir + "/noisyCosmic_" + str(runNum) + "_report.html"
    # self.outputFileNameClustered        = self.outputDir + "/noisyCosmic_" + str(runNum) + "_Clustered_report.html"
    # self.outputFileNameScatteredCluster = self.outputDir + "/noisyCosmic_" + str(runNum) + "_ScatteredCluster_report.html"
    self.dirs                           = dirs
    
    self.lookForStr   = "digi_occupancy_per_col_per_row_"    
    self.ROCThreshold = pixelThreshold
    
    self.pixelThreshold           = pixelThreshold

    self.clusterThreshold           = clusterThreshold
    self.pixelsInClusterThreshold = pixelsInClusterThreshold
    
    self.scatteredClusterRadius             = scatteredClusterRadius
    self.scatteredClusterThreshold          = scatteredClusterThreshold
    self.scatteredClusterNumberThreshold  = scatteredClusterNumberThreshold
    
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
  
    # OUT DIRECTORY
    if not os.path.exists(self.outputDir):
      os.system("mkdir " + self.outputDir)
      
    # RUN SPECIFIC OUT DIRECTORY
    if not os.path.exists(self.outputDir + "/" + str(self.runNum)):
      os.system("mkdir " + self.outputDir + "/" + str(self.runNum))
    
    with open(self.outputFileNames[0], "w") as outputFile:
      with open(self.outputFileNames[1], "w") as outputFileClustered:
        with open(self.outputFileNames[2], "w") as outputFileScatteredCluster:
      
          files = [outputFile, outputFileClustered, outputFileScatteredCluster]
          
          for f in files:
            f.write("<html><head></head><body>")
            f.write("<span style=\"font-size: large; font-weight: bold;\"> Noisy cosmic ROCs for the run: " + str(self.runNum) + "</br></span>")
      
      
          for layer in self.dicOfModuleHistograms:
            for f in files:
              f.write("</br> -> " + layer + "</br>")
              f.write("<table style=\"width: 700px;\">")
            
            for histObj in self.dicOfModuleHistograms[layer]:
              hist = histObj[0]
              histPath = histObj[1]
              
              maxVal = hist.GetMaximum()
              
              # SINGLE PIXEL CODE
              if maxVal >= self.pixelThreshold:
                linkPath = self.__BuildLink(histPath)
                files[0].write("<tr><td style=\"width: 500px;\">" + hist.GetName() + "</td><td style=\"width: 200px;\"><a href=\"" + linkPath + "\"> See plot</a></td></tr>")
              
              # CLUSTER FIND CODE
              if self.__DetermineCluster(hist, maxVal) == True:
                linkPath = self.__BuildLink(histPath)
                files[1].write("<tr><td style=\"width: 500px;\">" + hist.GetName() + "</td><td style=\"width: 200px;\"><a href=\"" + linkPath + "\"> See plot</a></td></tr>")
              
              # SCATTERED CLUSTER FIND CODE
              if self.__DetermineScatteredCluster(hist, maxVal) == True:
                linkPath = self.__BuildLink(histPath)
                files[2].write("<tr><td style=\"width: 500px;\">" + hist.GetName() + "</td><td style=\"width: 200px;\"><a href=\"" + linkPath + "\"> See plot</a></td></tr>")
              
            for f in files: 
              f.write("</table>")
          
          for f in files:          
            f.write("</body></html>")
              
  
###################################################################

for i in range(1, len(sys.argv)):
  if i == 1:
    runNumber = int(sys.argv[1])

runNumberStr = str(runNumber)

runStrHigh    = "000" + runNumberStr[0:2] + "x" * 4
runStrMedium  = "000" + runNumberStr[0:4] + "x" * 2

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

readerObj = NoisyROCsReader(runNumber, tmpFileName, outputDir, baseRootDir)
readerObj.AnalyzeHistograms()

print("*** Job done - removing temporary files ***")
os.system("rm " + tmpFileName)

print("Your reports are available in:")
print(outputDir + "/" + runNumberStr + "/")
  
