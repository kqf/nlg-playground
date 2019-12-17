import argparse
import sys
import numpy as np
from datetime import datetime
from sklearn.externals import joblib


def main():
    args = argparse.ArgumentParser(description="Generate text with a HMM")
    args.add_argument("-l", "--num-lines", type=int, default=1,
                      help="number of lines to generate")
    args.add_argument("-w", "--num-words", type=int, default=25,
                      help="number of words per line (excludes -d)")
    args.add_argument("--seed", type=int, default=datetime.now().microsecond)
    args.add_argument("filename", help="input filename")
    args = args.parse_args()
    model = joblib.load(args.filename)
    seed = args.seed
    for _i in range(args.num_lines):
        random_len = args.num_words
        seed = seed + 1

        symbols, _states = model.named_steps["multinomialhmm"].sample(
            random_len, random_state=seed)

        le = model.named_steps["textvectorizer"].le
        output = le.inverse_transform(np.squeeze(symbols))
        for word in output:
            print(word, end=" ")
        print()

    print("seed={0}".format(args.seed), file=sys.stderr)


if __name__ == '__main__':
    main()
