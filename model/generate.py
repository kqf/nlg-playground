import sys
import argparse
import joblib
from datetime import datetime


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
    sentence_sizes = [(args.num_words, args.seed)] * args.num_lines
    output = model.inverse_transform(sentence_sizes)
    print("Generated text:")
    print("\n".join(output))
    print("seed={0}".format(args.seed), file=sys.stderr)


if __name__ == '__main__':
    main()
