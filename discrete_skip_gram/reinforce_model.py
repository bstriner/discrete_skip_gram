"""
Columnar analysis. Parameters are p(z|x). Each batch is a set of buckets.
"""

import csv
import os

import numpy as np
import theano
import theano.tensor as T
from keras import backend as K
from tqdm import tqdm

from .tensor_util import save_weights, load_latest_weights


class ReinforceModel(object):
    def __init__(self,
                 cooccurrence,
                 z_k,
                 opt,
                 parameterization,
                 beta=0.02,
                 eps=1e-9):
        cooccurrence = cooccurrence.astype(np.float32)
        self.cooccurrence = cooccurrence
        self.z_k = z_k
        self.opt = opt
        self.parameterization = parameterization
        x_k = cooccurrence.shape[0]
        self.x_k = x_k

        # cooccurrence matrix
        n = np.sum(cooccurrence, axis=None)
        _co = cooccurrence / n
        co = T.constant(_co, name="co")  # (x_k, x_k)
        _co_m = np.sum(_co, axis=1, keepdims=True)
        co_m = T.constant(_co_m, name="co_m")  # (x_k,1)
        _co_c = _co / (eps + _co_m)
        _co_h = np.sum(_co * -np.log(eps + _co_c), axis=1, keepdims=True)  # (x_k, 1)
        print "COh: {}".format(np.sum(_co_h))
        co_h = T.constant(_co_h, name="co_h")

        logpz = self.parameterization.logpz
        encoding = self.parameterization.encoding

        # sampled conditional entropy
        b = T.zeros((z_k, x_k))
        b = T.set_subtensor(b[encoding, T.arange(x_k)], 1)  # one-hot encoding (z_k, x_k)
        pb = T.dot(b, co)
        m = T.sum(pb, axis=1, keepdims=True)
        c = pb / (m + eps)
        sampled_nll = T.sum(pb * -T.log(eps + c), axis=None)  # scalar
        avg_nll = K.variable(0., dtype='float32')
        new_avg = (beta * sampled_nll) + ((1. - beta) * avg_nll)
        avg_updates = [(avg_nll, new_avg)]

        theano.function([], [], updates=[(avg_nll, sampled_nll)])()

        # todo: check sign!
        sampled_loss = theano.gradient.zero_grad(sampled_nll - avg_nll) * logpz

        utilization = T.sum(T.gt(T.sum(b, axis=1), 0), axis=0)
        reg_loss = T.constant(0.)
        if parameterization.regularize:
            reg_loss = parameterization.loss
        loss = reg_loss + sampled_loss

        updates = opt.get_updates(loss=loss, params=parameterization.params)

        self.val_fun = theano.function([], [sampled_nll])
        self.encodings_fun = theano.function([], encoding)
        self.train_fun = theano.function([], [sampled_nll, reg_loss, loss, utilization], updates=updates + avg_updates)
        self.weights = parameterization.params + opt.weights + [avg_nll]

    def train_batch(self):
        return self.train_fun()

    def train(self, outputpath, epochs,
              batches):
        if not os.path.exists(outputpath):
            os.makedirs(outputpath)
        initial_epoch = load_latest_weights(outputpath, r'model-(\d+).h5', self.weights)
        if initial_epoch < epochs:
            with open(os.path.join(outputpath, 'history.csv'), 'ab') as f:
                w = csv.writer(f)
                w.writerow(['Epoch',
                            'Mean NLL',
                            'Min NLL',
                            'Mean Utilization',
                            'Min Utilization',
                            'Max Utilization',
                            'Regularization Loss',
                            'Loss'])
                f.flush()
                for epoch in tqdm(range(initial_epoch, epochs), desc="Training"):
                    it = tqdm(range(batches), desc="Epoch {}".format(epoch))
                    nlls = []
                    reg_losses = []
                    losses = []
                    utilizations = []
                    for _ in it:
                        nll, reg_loss, loss, utilization = self.train_batch()
                        nlls.append(nll)
                        reg_losses.append(reg_loss)
                        losses.append(loss)
                        utilizations.append(utilization)
                        it.desc = ("Epoch {}: " +
                                   "Mean NLL {:.4f} " +
                                   "Min NLL {:.4f} " +
                                   "Current NLL {:.4f} " +
                                   "Current Utilization {} " +
                                    "Mean Regularization Loss {:.4f} " +
                                   "Mean Loss {:.4f} " +
                                   "Current Loss {:.4f}").format(epoch,
                                                                 np.asscalar(np.mean(nlls)),
                                                                 np.asscalar(np.min(nlls)),
                                                                 np.asscalar(nll),
                                                                 np.asscalar(utilization),
                                                                 np.asscalar(np.mean(reg_losses)),
                                                                 np.asscalar(np.mean(losses)),
                                                                 np.asscalar(loss))
                    w.writerow([epoch,
                                np.asscalar(np.mean(nlls)),
                                np.asscalar(np.min(nlls)),
                                np.asscalar(np.mean(utilizations)),
                                np.asscalar(np.min(utilizations)),
                                np.asscalar(np.max(utilizations)),
                                np.asscalar(np.mean(reg_losses)),
                                np.asscalar(np.mean(losses))])
                    f.flush()
                    enc = self.encodings_fun()  # (n, x_k)
                    np.save(os.path.join(outputpath, 'encodings-{:08d}.npy'.format(epoch)), enc)
                    save_weights(os.path.join(outputpath, 'model-{:08d}.h5'.format(epoch)), self.weights)
