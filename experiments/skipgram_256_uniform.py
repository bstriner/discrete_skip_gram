import os

# os.environ["THEANO_FLAGS"]="optimizer=None,device=cpu"
import numpy as np
from keras.optimizers import Adam

from discrete_skip_gram.flat_validation import run_flat_validation
from discrete_skip_gram.initializers import uniform_initializer
from discrete_skip_gram.regularizers import EntropyRegularizer
from discrete_skip_gram.uniform_model import UniformModel


def main():
    epochs = 1000
    batches = 4096
    z_k = 256
    outputpath = "output/skipgram_256_uniform"
    cooccurrence = np.load('output/cooccurrence.npy').astype(np.float32)
    opt = Adam(1e-3)
    initializer = uniform_initializer(0.05)
    reg = EntropyRegularizer(1e-6)
    initial_b = np.log(np.sum(cooccurrence, axis=0))
    model = UniformModel(cooccurrence=cooccurrence,
                         z_k=z_k,
                         opt=opt,
                         pz_regularizer=reg,
                         initializer=initializer,
                         initial_b=initial_b)
    model.train(outputpath,
                epochs=epochs,
                batches=batches)
    return run_flat_validation(input_path=outputpath,
                               output_path=os.path.join(outputpath, "validate.txt"),
                               cooccurrence=cooccurrence)


if __name__ == "__main__":
    main()
