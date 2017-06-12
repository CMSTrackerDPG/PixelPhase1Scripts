#!/usr/bin/env python

import sys
import os
from ROOT import *
from copy import deepcopy
from array import array

import random
random.seed(1234567)

gROOT.SetBatch()        # don't pop up canvases

# Default values
outputDirectoryName = "OUT/"
detIDsFileName = "DATA/detids.dat"
                             
maxPxBarrel = 4
maxPxForward = 3
barrelLadderShift = [0, 14, 44, 90]

forwardDiskXShift = [25, 75, 125]
forwardDiskYShift = 45; # to make +DISK on top in the 'strip-like' layout

plotWidth, plotHeight = 6000, 4000
extremeBinsNum = 20

histNames = ["Sectors", "Blade-Ladder [M vs P][- vs +]", "Blade-Ladder [O vs I][- vs +]"]
histMinimum = [0, -32, -32]

class TH2PolyOfflineMaps:
   
  ############################################################################  
    
  def __AddNamedBins(self, geoFile, tX, tY, sX, sY, applyModuleRotation = False):

    for line in geoFile:
      lineSpl = line.strip().split("\"")
      
      detId = lineSpl[0].split(" ")[0]
      
      vertices = lineSpl[1]
      xy = vertices.split(" ")
      x, y = array('d'), array('d')
      verNum = 1
      for coord in xy:
        coordSpl = coord.split(",")
        if applyModuleRotation:
          x.append(-(float(coordSpl[0]) * sX + tX))
          y.append((float(coordSpl[1]) * sY + tY))
        else:
          x.append(float(coordSpl[0]) * sX + tX)
          y.append(float(coordSpl[1]) * sY + tY)
        verNum = verNum + 1
      #close polygon
      x.append(x[0])
      y.append(y[0])
      
      # print(detId, vertices)
      # print(x)
      # print(y)
      if applyModuleRotation:
        bin = TGraph(verNum, y, x)
      else:
        bin = TGraph(verNum, x, y)
      # bin = TGraph(verNum, y, x) # rotation by 90 deg (so that it had the same layout as for the strips)
      bin.SetName(detId)
      
      self.__BaseTrackerMap.AddBin(bin)
    
  def __CreateTrackerBaseMap(self):
  
    self.__BaseTrackerMap = TH2Poly("Summary", "", -10, 160, -70, 70)
    # self.__BaseTrackerMap = TH2Poly("Summary", "Tracker Map", 0, 0, 0, 0)
    self.__BaseTrackerMap.SetFloat(1)
    self.__BaseTrackerMap.GetXaxis().SetTitle("")
    self.__BaseTrackerMap.GetYaxis().SetTitle("")
    self.__BaseTrackerMap.SetOption("COLZ L")
    self.__BaseTrackerMap.SetStats(0)
  
    # BARREL FIRST
    for i in range(maxPxBarrel):
      with open(self.geometryFilenames[i], "r") as geoFile:
        currBarrelTranslateX = 0
        currBarrelTranslateY = barrelLadderShift[i]
        
        self.__AddNamedBins(geoFile, currBarrelTranslateX, currBarrelTranslateY, 1, 1, True)
      
      # break # debug only 1st layer
      
    # MINUS FORWARD
    for i in range(-maxPxForward, 0):
      with open(self.geometryFilenames[maxPxBarrel + maxPxForward + i], "r") as geoFile:
        currForwardTranslateX = forwardDiskXShift[-i - 1]
        currForwardTranslateY = -forwardDiskYShift
        
        self.__AddNamedBins(geoFile, currForwardTranslateX, currForwardTranslateY, 1, 1)
        
    # PLUS FORWARD
    for i in range(maxPxForward):
      with open(self.geometryFilenames[maxPxBarrel + maxPxForward + i], "r") as geoFile:
        currForwardTranslateX = forwardDiskXShift[i - 1]
        currForwardTranslateY = forwardDiskYShift
        
        self.__AddNamedBins(geoFile, currForwardTranslateX, currForwardTranslateY, 1, 1)
   
    # self.__BaseTrackerMap.Fill("305139728", 2)
    
    print("Base Tracker Map: constructed")
  
  def __DecodeThePart(self, thePart):
    if thePart[1:] == "mI":
      return 0
    if thePart[1:] == "mO":
      return 1
    if thePart[1:] == "pI":
      return 2
    if thePart[1:] == "pO":
      return 3
    
  def __DecodeOnlineName(self, online):
    onlineSpl = online.strip().split("_")
    
    if onlineSpl[0][0] == "B":
      thePart = self.__DecodeThePart(onlineSpl[1])
      sector = int(onlineSpl[2][3:])
      layer = int(onlineSpl[3][3:])
      ladder = int(onlineSpl[4][3:-1])
      module = int(onlineSpl[5][3:])
      
      return "B", thePart, sector, layer, ladder, module
    
    thePart = self.__DecodeThePart(onlineSpl[1])
    disk = int(onlineSpl[2][1:])
    blade = int(onlineSpl[3][3:])
    panel = int(onlineSpl[4][3:])
    ring = int(onlineSpl[5][3:])
    
    return "F", thePart, disk, blade, panel, ring
    
  def __GetDataForHistogramId(self, histId, detId):
    vals = self.__DecodeOnlineName(self.rawToOnlineDict[detId])
    
    if histId == 0:
      if vals[0] == "B":
        return vals[2]
      else:
        return 0
        
    elif histId == 1:
      if vals[0] == "B":
        return vals[4] * (1 if (vals[1] >> 1) else -1)
      else:
        return vals[3] * (1 if (vals[1] >> 1) else -1)
    
    elif histId == 2:
      if vals[0] == "B":
        return vals[4] * (-1 if vals[1] % 2 else 1)
      else:
        return vals[3] * (-1 if vals[1] % 2 else 1)
    
    else:
      return 0
   
  ############################################################################

  def __init__(self, outputDirName, modDicName):
    self.outputDirName = outputDirName
    self.detIDsFileName = modDicName
    
    self.geometryFilenames = []
    for i in range(maxPxBarrel):
      self.geometryFilenames.append("DATA/Geometry/vertices_barrel_" + str(i + 1))
    for i in range(-maxPxForward, maxPxForward + 1):
      if i == 0:
        continue #there is no 0 disk
      self.geometryFilenames.append("DATA/Geometry/vertices_forward_" + str(i))
    
    self.__CreateTrackerBaseMap()
    
    self.rawToOnlineDict = {} 
    with open(self.detIDsFileName, "r") as detIDs:  # create dictionary online -> rawid
      for entry in detIDs:
        items = entry.replace("\n", " ").split(" ")
        self.rawToOnlineDict.update({int(items[0]) : items[1]})
         
  def PrintTrackerMaps(self):
  
    # customColorIdxArr = [];
    # colorObjs = []
    # for i in range(61): 
      # ci = TColor.GetFreeColorIndex()
      # customColorIdxArr.append(ci)
      # R = random.randint(0, 255) / 255.0
      # G = random.randint(0, 255) / 255.0
      # B = random.randint(0, 255) / 255.0
      
      # print(ci, int(R * 255), int(G * 255), int(B * 255))
      
      # colorObjs.append(TColor(ci, R, G, B))
      
    # random.shuffle(customColorIdxArr)
    # print(customColorIdxArr)
    
    # gStyle.SetPalette(len(customColorIdxArr), array('i', customColorIdxArr))
    # gPad.Update()
    # num = 5
    # red, green, blue = [], [], []
    # stops = [1.0/(num - 1) * x for x in range(num)]
    # for i in range(num):
      # red.append(random.randint(0, 255) / 255.0)
      # green.append(random.randint(0, 255) / 255.0)
      # blue.append(random.randint(0, 255) / 255.0)
      
    # TColor.CreateGradientColorTable(num, array("d", stops), array("d", red), array("d", green), array("d", blue), num*10)
    
    gStyle.SetPalette(85)
   
    if os.path.exists(self.outputDirName) == False: # check whether directory exists
      os.system("mkdir " + self.outputDirName)
    
    ###################
    
    for i in range(len(histNames)):
    
      currentHist = deepcopy(self.__BaseTrackerMap)
      histoTitle = histNames[i]
      
      for detId in self.rawToOnlineDict:
        val = self.__GetDataForHistogramId(i, detId)
        currentHist.Fill(str(detId), val)
      
      c1 = TCanvas(histoTitle, histoTitle, plotWidth, plotHeight)
        
      currentHist.SetMarkerSize(0.25)
      # gStyle.SetHistMinimumZero()
      currentHist.SetMinimum(histMinimum[i])
        
      currentHist.Draw("A COLZ L TEXT45") # L - lines, TEXT - text       
            
      ### IMPORTANT - REALTIVE POSITIONING IS MESSY IN CURRENT VERION OF PYROOT
      ### IT CAN CHANGE FROM VERSION TO VERSION, SO YOU HAVE TO ADJUST IT FOR YOUR NEEDS
      ### !!!!!!!!!!!!!
            
      # draw axes (z, phi -> BARREL; x, y -> FORWARD)
      ###################################################
      
      ### z arrow
      arrow = TArrow(0.05, 27.0, 0.05, -30.0, 0.02, "|>")
      arrow.SetLineWidth(4)
      arrow.Draw()
      ### phi arrow
      phiArrow = TArrow(0.0, 27.0, 30.0, 27.0, 0.02, "|>")
      phiArrow.SetLineWidth(4)
      phiArrow.Draw()
      ### x arror
      xArrow = TArrow(25.0, 44.5, 50.0, 44.5, 0.02, "|>")
      xArrow.SetLineWidth(4)
      xArrow.Draw()
      ### y arror
      yArrow = TArrow(25.0, 44.5, 25.0, 69.5, 0.02, "|>")
      yArrow.SetLineWidth(4)
      yArrow.Draw()

      ###################################################
      
      # add some captions        
      txt = TLatex()
      txt.SetNDC()
      txt.SetTextFont(1)
      txt.SetTextColor(1)
      txt.SetTextAlign(22)
      txt.SetTextAngle(0)
      
      # draw new-style title
      txt.SetTextSize(0.05)
      txt.DrawLatex(0.5, 0.95, histoTitle)
      
      txt.SetTextSize(0.03)
      
      txt.DrawLatex(0.5, 0.125, "-DISK")
      txt.DrawLatex(0.5, 0.075, "NUMBER ->")
      txt.DrawLatex(0.5, 0.875, "+DISK")
      
      txt.DrawLatex(0.12, 0.35, "+z")
      txt.DrawLatexNDC(0.315, 0.665, "+phi") # WAY TO FORCE IT TO DRAW LATEX CORRECTLY NOT FOUND ('#' DOESN'T WORK)
      txt.DrawLatex(0.38, 0.73, "+x")
      txt.DrawLatex(0.235, 0.875, "+y")
      
      txt.SetTextAngle(90)
      txt.DrawLatex(0.125, 0.5, "BARREL")

      #save to the png
      c1.Print(self.outputDirName + histoTitle + ".png")
    
      
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--
    
readerObj = TH2PolyOfflineMaps(outputDirectoryName, detIDsFileName)  
readerObj.PrintTrackerMaps()
