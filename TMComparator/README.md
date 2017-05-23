TMComparator package
====================

The script was designed to find and track differences between Tracker Maps (especially between runs) that are available on vocms061 server. It makes great use of the PIL package. The result is a 2x2 matrix of Tracker Maps.

How to use it
-------------

The script requires input text file which contains information about Tracker Maps to analyze:

   1. Path to the reference ("source") Tracker Map.
   2. Path to the current ("destination") Tracker Map.
   3. Path (directory) to the output Tracker Map (optional, if not specified `/data/users/event_display/TMComparator/` will be used.

Paths to the source and destination Tracker Maps are assumed to be inside `/data/users/event_display/`.

Output file name is composed as follows: `comparisonImage_<source run number>vs<destination run number>.png`. The run number has to be able to be deducted from the input file path.

The difference between inputs can be calculated in two ways (you can control this behaviour by `-s` switch when you call the script):

   1. Absolute total difference between two images. Output colors depend on the primary content in each pixel, which can result in many different colors in the difference Tracker Map. As the fourth map the image which is a simple superimposition of the two inputs is created.
   2. (`-s`) Binary difference between two images. Tracker map has a single non black color wherever source and destination differ. The fourth image in that case is a difference-masked version of the destination Tracker Map.

Run the script
--------------

Example of the script calling:
`python script.py input.dat -s`
