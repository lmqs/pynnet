from pynnet.base import *

import imp

__all__ = ['load_dataset', 'DsetRef', 'DataRef']

class DsetRef(object):
    __slots__ = ('name', 'part', 'data')
    def __init__(self, name, part, shared_class=None):
        self.name = name
        self.part = part
        if shared_class:
            self.shared_class = shared_class
        else:
            self.shared_class = get_dset(self.name).shared_class
        self.data = get_dset(self.name).get(part)

    def __getitem__(self, portion):
        return DataRef(self, portion)

    def __reduce__(self):
        return DsetRef, (self.name, self.part)

class DataRef(object):
    __slots__ = ('dset', 'portion', 'data')
    def __init__(self, dset, portion):
        self.dset = dset
        self.portion = portion
        self.data = dset.data[portion]

    def _as_TensorVariable(self):
        return T.as_tensor_variable(self.data)

    def __reduce__(self):
        return DataRef, (self.dset, self.portion)

def load_dataset(name, part, portion=None):
    ref = DataRef(name, part)
    if portion:
        return ref[portion]
    else:
        return ref

_dset_cache = dict()
dset_path = ['.']

def get_dset(name):
    if name not in _dset_cache:
        try:
            fp, pathname, descr = imp.find_module(name, dset_path)
        except ImportError:
            raise AttributeError('No such dataset: ', + name)
        try:
            mod = imp.load_module(name, fp, pathname, descr)
        except ImportError:
            raise ValueError('Could not load dataset ' + name)
        finally:
            if fp:
                fp.close()
        _dset_cache[name] = mod
    return _dset_cache[name]
