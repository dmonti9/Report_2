
import sys, os


from MEM import *
from SVM import *

class ML_model:

    ## --------------------------------------------------
    ## Constructor: Load model from file
    ## --------------------------------------------------
    def __init__(self, modelfile, params=None):
        # if the model file exists, assume it is a trained model and load it
        # if it doesn't exist, create an empty model of the appropriate kind
        
        ext = modelfile[-4:]
        
        if params is None :
            # only modelfile given, load it            
            if ext == ".mem" : self._model = MEM(modelfile)
            elif ext == ".svm" : self._model = SVM(modelfile)

        else :
            # params given, create a new empty model
            if ext == ".mem" : self._model = MEM(modelfile, params)
            elif ext == ".svm" : self._model = SVM(modelfile, params)
        
        

    ## --------------------------------------------------
    ## Call trainer on a data file, save model
    ## --------------------------------------------------            
    def train(self, datafile) :
        return self._model.train(datafile)
            
    ## --------------------------------------------------
    ## Call predictor on a sequence
    ## --------------------------------------------------            
    def predict(self, xseq) :
        return self._model.predict(xseq)


