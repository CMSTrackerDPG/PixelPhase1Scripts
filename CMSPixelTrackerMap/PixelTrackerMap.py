#!/bin/env python

import pickle
import sys
from copy import deepcopy
import random

dataDir = "DATA/"
maxPxBarrel = 4
maxPxForward = 3

barrelSubShiftX, barrelSubShiftY = 30, 60
barrelScaleX, barrelScaleY = 4, -8
barrelLadderShift = [0, 14, 44, 90]

forwardScaleX, forwardScaleY = 8, -8

defaultFillColor = "255, 255, 255"

#################################################################### PIXEL TRACKER MAP

class PixelTrackerMap:
  def __init__(self, cablingInfoDetID, cablingInfoFEDID, inputFileName, detid_fedid_searchOption):
    self.geometryFilenames = []
    self.inputModules = {}
    self.SVGStream = ""
    # self.cablingInfoDetID = pickle.load(open("DATA/cablingDic.pkl" ,"rb"))
    self.cablingInfoDetID = cablingInfoDetID
    self.cablingInfoFEDID = cablingInfoFEDID
    self.detid_fedid_searchOption = detid_fedid_searchOption
    
    for i in range(maxPxBarrel):
      self.geometryFilenames.append("DATA/Geometry/vertices_barrel_" + str(i + 1))
    for i in range(-maxPxForward, maxPxForward + 1):
      if i == 0:
        continue #there is no 0 disk
      self.geometryFilenames.append("DATA/Geometry/vertices_forward_" + str(i))
    # print(self.geometryFilenames)
    with open(inputFileName, "r") as input:
      for line in input:
        lineSpl = line.strip().split(" ")
        if lineSpl[0] not in self.inputModules:
          if len(lineSpl) > 1:
            # self.inputModules.update({lineSpl[0] : "".join([lineSpl[1] + ", " + lineSpl[2] + ", " + lineSpl[3]])})
            R = str(random.randint(0, 256))
            G = str(random.randint(0, 256))
            B = str(random.randint(0, 256))
            self.inputModules.update({lineSpl[0] : "".join([R + ", " + G + ", " + B])})
          else:
            self.inputModules.update({lineSpl[0] : "255, 0, 0"})        
          
    # print(self.inputModules)
  def DrawMap(self):
    fillColor = ""
    
    # BARREL FIRST
    barrelSVGStream = ""
    for i in range(maxPxBarrel):
      with open(self.geometryFilenames[i], "r") as geoFile:
        currSVGStream = ""
        currBarrelTranslateX = 0
        currBarrelTranslateY = 0
        
        for line in geoFile:
          vertices, fillColor, dicInfo = self.__GetPolygonInfo(line)
            
          currSVGStream = currSVGStream + self.__BuildPolygon(vertices, fillColor, dicInfo)
          
        currBarrelTranslateY = currBarrelTranslateY + barrelLadderShift[i] * barrelScaleY
        
        barrelSVGStream = barrelSVGStream + self.__SavePolygonGroup(currSVGStream, currBarrelTranslateX, currBarrelTranslateY, barrelScaleX, barrelScaleY)
    
    self.SVGStream = self.SVGStream + "<g id=\"barrelPolygonGroup\">\n"
    self.SVGStream = self.SVGStream + "<g transform=\"rotate(90)\">\n"
    self.SVGStream = self.SVGStream + barrelSVGStream
    self.SVGStream = self.SVGStream + "</g>\n"
    self.SVGStream = self.SVGStream + "</g>\n"
    
    # MINUS FORWARD
    forwardSVGStream = ""
    for i in range(-maxPxForward, 0):
      with open(self.geometryFilenames[maxPxBarrel + maxPxForward + i], "r") as geoFile:
        currSVGStream = ""
        currForwardTranslateX = 0
        currForwardTranslateY = -(80) * forwardScaleY
        for line in geoFile:  
          vertices, fillColor, dicInfo = self.__GetPolygonInfo(line)
            
          currSVGStream = currSVGStream + self.__BuildPolygon(vertices, fillColor, dicInfo, False)

          currForwardTranslateX = (60 * (-0.95 - i)) * forwardScaleX

        forwardSVGStream = forwardSVGStream + self.__SavePolygonGroup(currSVGStream, currForwardTranslateX, currForwardTranslateY, forwardScaleX, forwardScaleY)   
        
    self.SVGStream = self.SVGStream + "<g id=\"mForwardPolygonGroup\">\n"
    self.SVGStream = self.SVGStream + forwardSVGStream
    self.SVGStream = self.SVGStream + "</g>\n"
    
    # PLUS FORWARD
    forwardSVGStream = ""
    for i in range(maxPxForward):
      with open(self.geometryFilenames[maxPxBarrel + maxPxForward + i], "r") as geoFile:
        currSVGStream = ""
        currForwardTranslateX = 0
        currForwardTranslateY = -(20) * forwardScaleY
        for line in geoFile:   
          vertices, fillColor, dicInfo = self.__GetPolygonInfo(line)
            
          currSVGStream = currSVGStream + self.__BuildPolygon(vertices, fillColor, dicInfo, False)

          currForwardTranslateX = (60 * (0.05 + i)) * forwardScaleX

        forwardSVGStream = forwardSVGStream + self.__SavePolygonGroup(currSVGStream, currForwardTranslateX, currForwardTranslateY, forwardScaleX, forwardScaleY) 
        
    self.SVGStream = self.SVGStream + "<g id=\"pForwardPolygonGroup\">\n"
    self.SVGStream = self.SVGStream + forwardSVGStream
    self.SVGStream = self.SVGStream + "</g>\n"
    
    self.__PrintHeader()
    print(self.SVGStream)
    self.__PrintFooter()
    
  def __GetPolygonInfo(self, line):
    rawId = line.strip().split(" ")[0]
    onlineId = line.strip().split(" ")[1]
    vertices = line.strip().split("\"")[1]
    infoDic = {"detId" : rawId, "oid" : onlineId}
    
    if self.detid_fedid_searchOption == "fedid":
      fedid = (self.cablingInfoDetID[rawId])["FED ID"]  # if CMSSW would not fire it will crash on the first barrel element
      if fedid in self.inputModules:
        fillColor = self.inputModules[fedid]          
      else:
        fillColor = defaultFillColor
        
    else: #detid    
      if rawId in self.inputModules:
        fillColor = self.inputModules[rawId]          
      else:
        fillColor = defaultFillColor
      
    if rawId in self.cablingInfoDetID:
      infoDic = self.cablingInfoDetID[rawId]
      infoDic.update({"oid" : onlineId})
      
    return vertices, fillColor, infoDic
  
  def __BuildPolygon(self, vertices, fillColor, dic, isBarrel=True):
    ret = "<polygon "
    
    ret = ret + "points=\"" + vertices + "\" "
    ret = ret + "fill=\"rgb(" + fillColor + ")\" "
    ret = ret + "class=\"" + ("barrelPoly" if isBarrel else "forwardPoly") + "\" "
    
    for k in dic:
      ret = ret + ''.join(k.split(" ")) + "=\"" + dic[k] + "\" "
    
    ret = ret + "onclick=\"showData(evt);\" onmouseover=\"showData(evt);\" onmouseout=\"showData(evt);\" "
    
    ret = ret + "/>\n"
    return ret
    
  def __SavePolygonGroup(self, polygons, tX, tY, sX, sY):
    ret = ""
    ret = ret + "<g transform=\"translate(" + str(tX) + ", " + str(tY) + ")\">\n"
    ret = ret + "<g transform=\"scale(" + str(sX) + ", " + str(sY) + ")\">\n"
    ret = ret + polygons
    ret = ret + "</g>\n"
    ret = ret + "</g>\n"  
    return ret
  def __PrintHeader(self):
    print("<?xml version=\"1.0\" standalone=\"no\"?>")
    print("<?xml-stylesheet type=\"text/css\" href=\"DATA/SVGViewer/style.css\"?>")
    print("<svg xmlns=\"http://www.w3.org/2000/svg\"")
    print("xmlns:svg=\"http://www.w3.org/2000/svg\"")
    print("xmlns:xlink=\"http://www.w3.org/1999/xlink\" >")
    print("<script type=\"text/ecmascript\" xlink:href=\"DATA/SVGViewer/dynamic.js\" />")
    print("<svg id=\"mainMap\" x=\"0\" y=\"0\" onload=\"PixelTrackerShow.init()\">")
    print("<g id=\"allGeometryGroup\" style=\"transform: scale(0.7);\"   >")
  def __PrintFooter(self):
    print("</g>")
    print("</svg>")
    
    print("<rect class=\"tooltip_bg\" id=\"tooltip_bg\" rx=\"4\" ry=\"4\" width=\"52\" height=\"80\" visibility=\"hidden\"/>")
    # print("<text class=\"tooltip\" id=\"tooltip\" visibility=\"hidden\">")
    # print("<tspan id=\"line1\"> </tspan> ")
    # print("</text>")
    
    interestingQuantities = ["FEDID", "FEDposition", "FEDchannel"]
    
    print("<foreignObject id=\"infoTable\" visibility=\"hidden\"  x=\"100\" y=\"100\" width=\"350\" height=\"300\" >")
    print("<body xmlns=\"http://www.w3.org/1999/xhtml\">")
    print("<tspan id=\"moduleName\"> </tspan> ")
    print("<div class=\"myGrid\" >")
    
    for i in interestingQuantities: 
      print("<div class=\"myGridCellTh\" id=\"" + i + "\">" + i + "</div> ")
      print("<div class=\"myGridCell\" id=\"" + i +  "_val\"></div> ")
      
    print("</div>")
    print("</body>")
    print("</foreignObject>")
    
    print("</svg>")
    
######################################################################## LOAD PARAMS

inputName = "inputForPixelTrackerMap.dat"
fedDBInfoFileName = ""
detid_fedid_searchOption = "rawid"
outDicTxtFileName = "/tmp/tmptmp.tmp"
if len(sys.argv) > 1:
  inputName = sys.argv[1]
  fedDBInfoFileName = sys.argv[2]
  detid_fedid_searchOption = sys.argv[3]
  outDicTxtFileName = sys.argv[4]
    
######################################################################## DIC BUILDER

cablingFileName = "DATA/CablingDB/pxCabl.csv"
detIdDicFileName = "DATA/detids.dat"

pixelCablingInfoDic = {}
pixelCablingInfoDicFed = {}
detIdDic = {}

with open(detIdDicFileName, "r") as inputDic:
  for line in inputDic:
    l = line.strip()
    if len(l) > 0:
      strSpl = l.split()
      detIdDic.update({strSpl[1] : strSpl[0]})

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
      # FEDID DICTIONARY
      if fedId in pixelCablingInfoDicFed:
        pixelCablingInfoDicFed[fedId].update(tmpDic);
      else:
        pixelCablingInfoDicFed.update({fedId : tmpDic})
      
# update data using information grabbed from CMSSWDB
if fedDBInfoFileName != "":
  with open(fedDBInfoFileName, "r") as inputDBCabl:
    for line in inputDBCabl:
      strSpl = line.split(" ");
      
      detId = strSpl[0]
      fedId = strSpl[1]
      fedCh = (strSpl[2].strip())[0:-1]
      
      if detId in pixelCablingInfoDic:
        pixelCablingInfoDic[detId]["FED ID"] = fedId;
        pixelCablingInfoDic[detId]["FED channel"] = fedCh;
      else:
        tmpDic = {};
        tmpDic.update({"detId" : detId})
        tmpDic.update({"FED ID" : fedId})
        tmpDic.update({"FED channel" : fedCh})
        
        pixelCablingInfoDic.update({detId : tmpDic})

# save pixelCablingInfoDic to the textfile
with open(outDicTxtFileName, "w") as tmpFile:
  for k in pixelCablingInfoDic:
    dic = pixelCablingInfoDic[k]
    s = dic["detId"] + " "
    for k2 in sorted(dic): 
      s = s + k2 + ":" + dic[k2] + ", "
    tmpFile.write(s + "\n")

#################################################################### CALL MAIN STAFF 

obj = PixelTrackerMap(pixelCablingInfoDic, pixelCablingInfoDicFed, inputName, detid_fedid_searchOption)
obj.DrawMap()  