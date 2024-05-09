#!/usr/bin/env python3

import sys
from ML_model import *
from dataset import *


datafile = sys.argv[1]
modelfile = sys.argv[2]

# load data to annotate
ds = Dataset(datafile)
# load trained model to use
model = ML_model(modelfile)
    
for ex in ds.instances():
    # process each example and get predicted label
    pred = model.predict(ex["features"])
    if pred != "null" :
        print(ex["sid"],ex["e1"],ex["e2"],pred[0], sep="|")
