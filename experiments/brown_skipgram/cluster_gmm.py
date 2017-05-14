from discrete_skip_gram.clustering.utils import write_encodings
from discrete_skip_gram.clustering.gmm import cluster_gmm
from discrete_skip_gram.models.util import latest_model
import numpy as np
from dataset_util import load_dataset


def main():
    path = "output/skipgram_baseline"
    file, epoch = latest_model(path, "encodings-(\\d+).npy")
    print "Loading epoch {}: {}".format(epoch, file)
    z = np.load(file)
    z_depth = 10
    enc = cluster_gmm(z, z_depth)
    ds = load_dataset()
    output_path = "output/cluster_gmm/encodings"
    write_encodings(enc, ds, output_path)


if __name__ == "__main__":
    main()
