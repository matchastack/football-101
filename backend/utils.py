import pickle

def store_pkl(fname, object):
    with open(fname, 'wb') as f:
        pickle.dump(object, f)
    return

def load_pkl(fname):
    with open(fname, 'rb') as f:
        return pickle.load(f)
