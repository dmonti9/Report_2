
import scipy

class Dataset :
    # -----  load dataset (already converted to feature vectors),
    # -----  and create feature index
    def __init__(self, datafile) :
        self.examples = []
        self.fidx = {}
        nf = 0
        with open(datafile) as df :
            for line in df.readlines() :
                line = line.strip().split()
                sid,e1,e2,label = line[0:4]
                features = line[4:]
                self.examples.append({"sid":sid, "e1":e1, "e2": e2, "label": label, "features": features})
                # add features to index
                for f in features :
                    if f not in self.fidx :
                        self.fidx[f] = len(self.fidx)

    ## ------ allow access to feature index
    def feature_index(self) :
        return self.fidx 

    ## ------ return dataset as a sparse matrix, plus associated gold labels
    def csr_matrix(self) :
        rowi = [] # row (example number)
        colj = [] # column (feature number)
        data = [] # value (1 or 0 since we use binary features)
        Y = [] # ground truth
        nex = 0 # example  counter (each word is one example)

        # for each example
        for ex in self.examples :
            Y.append(ex["label"])
            for f in ex["features"] :
                data.append(1)
                rowi.append(nex)
                colj.append(self.fidx[f]) 
            # next example
            nex += 1
            
        X = scipy.sparse.csr_matrix((data, (rowi, colj)))  
        return X,Y
                
    ## ------ iterator to access each example in the dataset
    def instances(self) :
        for ex in self.examples :
            yield ex
