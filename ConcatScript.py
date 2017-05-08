#!/bin/env python

inFileNames = ["pxBmI.csv", "pxBmO.csv", "pxBpI.csv", "pxBpO.csv"]
path = "DATA/CablingDB/"
outFile = "DATA/CablingDB/pxCabl.csv"

isFirstFile = True

# with open(outFile, "w") as outFile:
for fileName in inFileNames:
  with open(path + fileName, "r") as inFile:
    isFirstLine = True
    for line in inFile:
      if line[0] == ",":
        continue
      if isFirstLine and not isFirstFile:
        # print(line)
        isFirstLine = False
        continue
      
      # outFile.write(line)
      print(line.strip())
      isFirstLine = False
  isFirstFile = False