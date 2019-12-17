import click
import sys
import numpy as np

import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import make_pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from hmmlearn import hmm
from nltk import FreqDist


class TextVectorizer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.le = LabelEncoder()
        self.fd = None

    def fit(self, X, y=None):
        self.le = LabelEncoder()
        self.le.fit(list(set(X)))
        self.fd = FreqDist(self.le.transform(X))
        return self

    def transform(self, X):
        labels = np.atleast_2d(
            np.fromiter(self.le.transform(X), np.int64)).T
        return labels


class DumpTrasformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        print("The dataset shape", X.shape)
        return X


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
@click.option('--output', '-o', default="artifacts/")
@click.option('--inputs', default=sys.stdin, required=True)
def main(modelname, num_states, output, inputs):
    np.random.seed(seed=None)
    # args = args.parse_args()
    lines = [line.split() for line in inputs]
    words = [word.lower() for line in lines for word in line]
    lengths = [len(line) for line in lines]

    model = make_pipeline(
        TextVectorizer(),
        DumpTrasformer(),
        MODELS[modelname](num_states),
    )
    model = model.fit(words, lengths)
    modelname = "{}.{}.{}.pkl".format(output, modelname, num_states)
    print("Saving the model: {}".format(modelname))
    joblib.dump(model, modelname)
