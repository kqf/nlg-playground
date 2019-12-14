import click
import sys
import pickle
import numpy as np

import joblib
from sklearn.preprocessing import LabelEncoder
from hmmlearn import hmm
from nltk import FreqDist


def warn(msg):
    print(msg, file=sys.stderr)


def outfile(output, model, num_states, ext):
    return "{name}.{model}.{n}.{ext}".format(
        name=output, model=model, n=num_states, ext=ext)


def builtin(num_states):
    warn("Initial parameter estimation using built-in method")
    model = hmm.MultinomialHMM(n_components=num_states, init_params='ste')
    return model


def frequencies(fd, alphabet, num_states):
    warn("Initial parameter estimation using relative frequencies")

    frequencies = np.fromiter(
        (fd.freq(i)
         for i in range(len(alphabet))), dtype=np.float64)
    emission_prob = np.stack([frequencies] * num_states)
    model = hmm.MultinomialHMM(n_components=num_states, init_params='st')
    model.emissionprob_ = emission_prob
    return model


def flat():
    return None


MODELS = {
    "builtin": builtin,
    "freq": frequencies,
    "flat": flat,
}


@click.command()
@click.option('--num-states', '-n', default=1, type=int)
@click.option(
    '--modelname', '-m', default='builtin',
    type=click.Choice(list(MODELS.keys())),
)
@click.option('--output', '-o', default="demo/hmm")
@click.option('--inputs', default=sys.stdin, required=True)
def main(modelname, num_states, output, inputs):
    np.random.seed(seed=None)
    # args = args.parse_args()
    lines = [line.split() for line in inputs]
    words = [word.lower() for line in lines for word in line]

    alphabet = set(words)
    le = LabelEncoder()
    le.fit(list(alphabet))

    seq = le.transform(words)
    features = np.fromiter(seq, np.int64)
    features = np.atleast_2d(features).T
    fd = FreqDist(seq)

    model = MODELS[modelname](num_states)

    lengths = [len(line) for line in lines]
    print(features)
    model = model.fit(features, lengths)

    print(outfile(output, modelname, num_states, "pkl"))
    joblib.dump(model, outfile(output, modelname, num_states, "pkl"))
    with open(outfile(output, modelname, num_states, "le"), "wb") as f:
        pickle.dump(le, f)

    with open(outfile(output, modelname, num_states, "freqdist"), "wb") as f:
        pickle.dump(fd, f)

    warn("Output written to:\n\t- {0}\n\t- {1}\n\t- {2}".format(
        outfile(output, modelname, num_states, "pkl"),
        outfile(output, modelname, num_states, "le"),
        outfile(output, modelname, num_states, "freqdist")
    ))
