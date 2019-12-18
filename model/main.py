import click
import sys
import numpy as np
from datetime import datetime

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

    def inverse_transform(self, X):
        output = []
        for sentence in X:
            output.append(" ".join(self.le.inverse_transform(sentence)))
        return output


class DumpTrasformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        print("The dataset shape", X.shape)
        return X

    def inverse_transform(self, X):
        return X


class HMMTransformer(hmm.MultinomialHMM):
    def inverse_transform(self, X):
        output = []
        for i, (seqsize, seed) in enumerate(X):
            symbols, _states = self.sample(seqsize, random_state=seed + i)
            output.append(np.squeeze(symbols))
        return output


def builtin(num_states):
    model = hmm.MultinomialHMM(n_components=num_states, init_params='ste')
    return model


def frequencies(fd, alphabet, num_states):

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
def train(modelname, num_states, output, inputs):
    np.random.seed(seed=None)
    lines = [line.split() for line in inputs]
    words = [word.lower() for line in lines for word in line]
    lengths = [len(line) for line in lines]

    model = make_pipeline(
        TextVectorizer(),
        DumpTrasformer(),
        HMMTransformer(n_components=num_states, init_params='ste'),
    )
    model = model.fit(words, lengths)
    modelname = "{}.{}.{}.pkl".format(output, modelname, num_states)
    print("Saving the model: {}".format(modelname))
    joblib.dump(model, modelname)


@click.command()
@click.option('--num-lines', '-l', default=20, type=int)
@click.option('--num-words', '-w', default=10, type=int)
@click.option('--seed', type=int, default=datetime.now().microsecond)
@click.option('--filename', type=str, required=True)
def generate(num_lines, num_words, seed, filename):
    model = joblib.load(filename)
    sentence_sizes = [(num_words, seed)] * num_lines
    output = model.inverse_transform(sentence_sizes)
    print("Generated text:")
    print("\n".join(output))
    print("seed={0}".format(seed))
