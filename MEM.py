#####################################################
## Class to store an ngram ME model
#####################################################
import sys
import pickle

import scipy
import sklearn
from sklearn.linear_model import LogisticRegression

import dataset


class MEM:

    ## --------------------------------------------------
    ## Constructor: Load model from file
    ## --------------------------------------------------
    def __init__(self, modelfile, params=None):

        self.modelfile = modelfile
        if params is None:
            # only modelfile given, assume it is an existing model and load it        
            with open(self.modelfile, 'rb') as df :
                self.tagger = pickle.load(df)
            with open(self.modelfile+".idx", 'rb') as df :
                self.fidx = pickle.load(df)
                
        else :
            # params given, create new empty model

            # extract parameters if provided. Use default if not
            if params is None : params={}            
            C = float(params['C']) if 'C' in params else 1.0
            solver = params['solver'] if 'solver' in params else 'lbfgs'

            # create and train empty classifier with given parameters
            self.tagger = LogisticRegression(verbose=1,
                                             C=C,
                                             solver=solver,
                                             max_iter=1500,
                                             n_jobs=8)

                
    ## --------------------------------------------------
    ## train a model on given data, store in modelfile
    ## --------------------------------------------------
    def train(self, datafile):
        # load dataset
        ds = dataset.Dataset(datafile)
        self.fidx = ds.feature_index()

        # Read training instances 
        X,Y = ds.csr_matrix()

        # train classifier
        self.tagger.fit(X,Y)

        # save model
        pickle.dump(self.tagger, open(self.modelfile, 'wb'))
        pickle.dump(self.fidx, open(self.modelfile+".idx", 'wb'))
    

    ## --------------------------------------------------
    ## predict best class for given example
    ## --------------------------------------------------
    def predict(self, x):
        # Encode xseq into a CSR sparse matrix
        rowi = [] # row (example number)
        colj = [] # column (feature number)
        data = [] # value (1 or 0 since we use binary features)
        for f in x :
            if f in self.fidx :
                data.append(1)
                rowi.append(0) # we are labeling only one example
                colj.append(self.fidx[f]) 
            
        X = scipy.sparse.csr_matrix((data, (rowi, colj)), shape=(1,len(self.fidx)))
        
        # apply model to X and return predictions
        return self.tagger.predict(X)

