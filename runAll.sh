#!/bin/bash

python ConcatScript.py
python DicBuilder.py
python PixelTrackerMap.py $1 > $2