#!/usr/bin/env python3

import os,sys
from ML_model import *

# get file where model will be written
datafile = sys.argv[1]
modelfile = sys.argv[2]

# get parameters in line.  e.g. C=10 kernel=rbf degree=2
params = {}
pars = sys.argv[3:]
for x in pars:
    par,val = x.split("=")
    params[par] = val

# Create an empty model
model = ML_model(modelfile, params)

# Train and store the model
model.train(datafile)
