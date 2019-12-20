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

    def fit(self, X, y=None):
        self.le.fit(list(set(X)))
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


class DebugTrasformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        print("The dataset shape", X.shape)
        return X

    def inverse_transform(self, X):
        return X


class HMMTransformer(hmm.MultinomialHMM):
    def __init__(self, *args, **kwargs):
        super(HMMTransformer, self).__init__(*args, **kwargs)
        self.fd_ = None
        self.sampling_method = "hmm"

    def fit(self, X, y, **kwargs):
        self.fd_ = FreqDist(X.reshape(-1))
        super(HMMTransformer, self).fit(X, y, **kwargs)
        return self

    def inverse_transform(self, X):
        output = []
        keys, probs = zip(*((k, self.fd_.freq(k)) for k in self.fd_.keys()))
        for i, (seqsize, seed) in enumerate(X):
            if self.sampling_method == 'hmm':
                symbols, _states = self.sample(seqsize, random_state=seed + i)
            elif self.sampling_method == "freq":
                symbols = np.random.choice(keys, size=seqsize, p=probs)
            elif self.sampling_method == "random":
                symbols = np.random.choice(keys, size=seqsize)
            else:
                raise IOError("No such sampling method", self.sampling_method)
            output.append(np.squeeze(symbols))
        return output


@click.command()
@click.option('--num-states', '-n', default=1, type=int)
@click.option('--modelname', '-m', default='builtin', type=str)
@click.option('--output', '-o', default="artifacts/")
@click.option('--inputs', default=sys.stdin, required=True)
def train(modelname, num_states, output, inputs):
    np.random.seed(seed=None)
    lines = [line.split() for line in inputs]
    words = [word.lower() for line in lines for word in line]
    lengths = [len(line) for line in lines]

    params = {
        "n_components": num_states,
        "init_params": "st",
        "verbose": True,
    }

    model = make_pipeline(
        TextVectorizer(),
        DebugTrasformer(),
        HMMTransformer(**params),
    )
    model.fit(words, lengths)
    modelname = "{}.{}.{}.pkl".format(output, modelname, num_states)
    print("Saving the model to {}".format(modelname))
    joblib.dump(model, modelname)


@click.command()
@click.option('--num-lines', '-l', default=10, type=int)
@click.option('--num-words', '-w', default=10, type=int)
@click.option('--seed', type=int, default=datetime.now().microsecond)
@click.option('--method', '-m', default="hmm", type=str)
@click.option('--filename', type=str, required=True)
def generate(num_lines, num_words, seed, method, filename):
    model = joblib.load(filename)
    sentence_sizes = [(num_words, seed)] * num_lines
    model.named_steps["hmmtransformer"].sampling_method = method
    output = model.inverse_transform(sentence_sizes)
    print("Generated text:")
    print("\n".join(output))
    print("seed={0}".format(seed))
