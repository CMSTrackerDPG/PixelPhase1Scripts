import os, sys, getopt
import Image
import ImageFont
import ImageDraw
import ImageChops
from copy import deepcopy

basePath = "/data/users/event_display/"

savePath = basePath + "TMComparator/"

mapBackgroundColor = (124, 153, 209)
binaryDifferenceColor = (39, 48, 150)

op = 0.5

yShift = 411
xShift = 343

useSimpleColorDiff = False

inputDataFileName = "input.dat"

#############################################

class TMComparator:
    def __init__(self, inputFileName):

        self.inputImages = []
        self.paths = []
        self.savePath = savePath

        with open(inputFileName, "r") as file:
            for i, line in enumerate(file):
                if i < 2:
                    self.inputImages.append(Image.open(basePath + line.strip()))
                    self.paths.append(line.strip().split("/"))
                elif len(line.strip()):
                    if i == 2:
                        self.savePath = line.strip()

        cleanRef = Image.open("DATA/white.png")
        self.inputImages.append( Image.eval(cleanRef, lambda x: 0 if x==255 else x) )

        # im.show()
        self.currSize = self.inputImages[0].size
       # print("%d x %d" % self.currSize)

        self.bbox = (2, yShift, self.currSize[0] - xShift, self.currSize[1] - 2)
        self.regions = [self.inputImages[i].crop(self.bbox) for i in range(len(self.inputImages))]
       # self.refRegion = cleanRef.crop(bbox)

        self.finalImage = Image.new("RGB", size = (self.currSize[0] * 2, self.currSize[1] * 2), color = mapBackgroundColor)

        for i in range(2):
            self.finalImage.paste(self.inputImages[i], (0, self.currSize[1] * i))

        self.font = ImageFont.truetype("DATA/barial.ttf",115)

    def process(self):

        srcRun = self.paths[0][3]
        dstRun = self.paths[1][3]
        quantity = self.paths[0][-1].split(".")[0]
        textToDraw = ("BINARY " if useSimpleColorDiff else "") + "DIFFERENCE BETWEEN " + srcRun + " AND " + dstRun + " FOR " + quantity
        textWidthHeight = self.font.getsize(textToDraw)
        myDraw = ImageDraw.Draw(self.finalImage)
        myDraw.text( (self.currSize[0] * 1.5  - textWidthHeight[0] * 0.5, 100), textToDraw, fill = (0, 0, 0), font = self.font)
        del myDraw

        if useSimpleColorDiff:
            #ONE COLOR FOR ALL DIFFERENCES

            myDiff = ImageChops.subtract(self.regions[0], self.regions[1])
            for i in range(myDiff.size[0]):
                for j in range(myDiff.size[1]):
                    # print(i, j)
                    px = myDiff.getpixel((i, j))
                    if px[0] != 0 or px[1] != 0 or px[2] != 0:
                        myDiff.putpixel((i, j), binaryDifferenceColor)

                        self.regions[1].putpixel((i, j), binaryDifferenceColor) # create difference-masked image

            myDiff = ImageChops.add(myDiff, self.regions[2])

            self.finalImage.paste(self.regions[1], (self.currSize[0], self.currSize[1] + yShift))

            textToDraw = "DIFFERENCE-MASKED TRACKER MAP FOR RUN " + dstRun   

        else:
            ###MANY COLORS INDICATE MANY POSSIBLE DIFFERENCES
            myDiff = ImageChops.subtract(self.regions[0], self.regions[1])
            myDiff = ImageChops.add(myDiff, self.regions[2]) #2 - refRegion

            blendedImage = Image.blend(self.regions[0], self.regions[1], op)
            self.finalImage.paste(blendedImage, (self.currSize[0], self.currSize[1] + yShift))
    
            textToDraw = "SUPERIMPOSED TRACKER MAPS"

        textWidthHeight = self.font.getsize(textToDraw)
        myDraw = ImageDraw.Draw(self.finalImage)
        myDraw.text( (self.currSize[0] * 1.5  - textWidthHeight[0] * 0.5,  self.currSize[1] + 100), textToDraw, fill = (0, 0, 0), font = self.font)
        del myDraw


        self.finalImage.paste(myDiff, (self.currSize[0],  yShift))

        outputFileName = self.savePath + "comparisonImage_" + srcRun + "vs" + dstRun + ".png"
        print(outputFileName)
        self.finalImage.save(outputFileName)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

if len(sys.argv) > 1:
    inputDataFileName = sys.argv[1]
    if len(sys.argv) > 2:
        opts, args = getopt.getopt(sys.argv[2:], "s", ["help", "output="])
        for o, a in opts:
            if o == "-s":
                useSimpleColorDiff = True

cmp = TMComparator(inputDataFileName) 
cmp.process()
