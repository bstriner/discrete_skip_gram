import numpy as np
from discrete_skip_gram.flat_train import train_flat_regularizer_battery
from discrete_skip_gram.regularizers import ExclusiveLasso


# os.environ["THEANO_FLAGS"]="optimizer=None,device=cpu"

def main():
    epochs = 10
    batches = 4096
    z_k = 256
    iters = 1
    outputpath = "output/skipgram_256-el"
    cooccurrence = np.load('output/cooccurrence.npy').astype(np.float32)
    weights = [
        1e-7,
        1e-8,
        1e-9,
        1e-10,
        1e-11,
        1e-12,
        1e-13
    ]
    regularizers = [ExclusiveLasso(w) for w in weights]
    labels = ["el-{:.01e}".format(w) for w in weights]
    train_flat_regularizer_battery(
        outputpath=outputpath,
        cooccurrence=cooccurrence,
        epochs=epochs,
        batches=batches,
        iters=iters,
        z_k=z_k,
        labels=labels,
        regularizers=regularizers,
        is_weight_regularizer=True,
        kwdata={'weights': np.array(weights)}
    )


if __name__ == "__main__":
    main()
