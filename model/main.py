import click
import sys
import numpy as np
from datetime import datetime

import joblib
# from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from hmmlearn import hmm
# from nltk import FreqDisd


class TextVectorizer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.le = CountVectorizer(min_df=0, analyzer="char")

    def fit(self, X, y=None):
        corpus = ["".join(chars) for chars in X]
        self.le.fit(corpus)
        return self

    def transform(self, X):
        return np.vstack([self.le.transform(w).todense() for w in X])

    def inverse_transform(self, X):
        output = []
        for sentence in X:
            output.append("".join(
                np.concatenate(self.le.inverse_transform(sentence)))
            )
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
        # self.fd_ = FreqDist(X.reshape(-1))
        if 'e' not in self.init_params.lower():
            probs = np.fromiter(self.fd_.values(), dtype=np.float)
            self.emissionprob_ = np.broadcast_to(
                probs / np.sum(probs),
                (self.n_components, len(probs)))
        super(HMMTransformer, self).fit(X, y, **kwargs)
        return self

    def inverse_transform(self, X):
        output = []
        for i, (seqsize, seed) in enumerate(X):
            if self.sampling_method == 'hmm':
                symbols, _states = self.sample(seqsize, random_state=seed + i)
            elif self.sampling_method == "freq":
                keys, probs = zip(*self.fd_.items())
                symbols = np.random.choice(keys, size=seqsize, p=probs)
            elif self.sampling_method == "random":
                keys, probs = zip(*self.fd_.items())
                symbols = np.random.choice(keys, size=seqsize)
            else:
                raise IOError("No such sampling method", self.sampling_method)
            output.append(np.squeeze(symbols))
        return np.array(output)


@click.command()
@click.option('--num-states', '-n', default=1, type=int)
@click.option('--output', '-o', default="artifacts/")
@click.option('--inputs', default=sys.stdin, required=True)
def train(num_states, output, inputs):
    np.random.seed(seed=None)
    lines = [list(line) for line in inputs]
    lengths = [len(line) for line in lines]
    print(lines, lengths)

    params = {
        "n_components": num_states,
        "init_params": "ste",
        "n_iter": 20,
        "verbose": True,
    }

    model = make_pipeline(
        TextVectorizer(),
        DebugTrasformer(),
        HMMTransformer(**params),
    )
    model.fit(lines, lengths)
    print("Saving the model to {}".format(output))
    joblib.dump(model, output)


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


@click.command()
@click.option('--filename', type=str, required=True)
@click.option('--inputs', default=sys.stdin, required=True)
def dialogue(filename, inputs):
    lines = [line.lower() for line in inputs]
    lengths = [len(line) for line in lines]
    model = joblib.load(filename)

    preds = np.squeeze(model.predict(lines, lengths=lengths))
    print(preds)
    print(model.named_steps["textvectorizer"].le.inverse_transform(preds))
