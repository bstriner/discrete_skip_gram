import sys
import os

sys.path.append(os.path.dirname(__file__))
import skipgram_flat_train
import skipgram_flat_b_train
import skipgram_flat_el_train
import skipgram_flat_l1_train
import skipgram_flat_l2_train

def main():
    skipgram_flat_train.main()
    skipgram_flat_b_train.main()
    skipgram_flat_el_train.main()
    skipgram_flat_l1_train.main()
    skipgram_flat_l2_train.main()

if __name__=="__main__":
    main()