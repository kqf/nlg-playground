import random
import logging
import os
import json
import markovify

import numpy as np
from collections import defaultdict
from mega import Mega
from environs import Env

logger = logging.getLogger(__name__)

env = Env()
env.read_env()


def from_env(sample):
    tokens = sample.split()
    ntokens = np.random.poisson(2)
    return " ".join(random.sample(tokens, min(len(tokens), ntokens)))


def lenglth_handler(update, context, history):
    msg = history[-1]
    if len(msg) < 3 and msg not in env.str("HANDLER_BIGRAMS").split():
        return from_env(env.str("HANDLER_LENGTH"))
    return None


def repetition_handler(update, context, history):
    if len(history) > 1 and history[-1] == history[-2]:
        return ""
    return None


def heuristics(update, context, history):
    handlers = [
        repetition_handler,
        lenglth_handler,
    ]
    for handler in handlers:
        message = handler(update, context, history)
        if message is not None:
            return message
    return None


class ReplyBot:
    def __init__(self, filename, model_url):
        self.model = None
        try:
            filename = self._download(filename, model_url)
            with open(filename, encoding='utf-8') as f:
                self.model = markovify.Text.from_json(json.load(f))
        except FileNotFoundError:
            logger.error(f"Model file {filename} is missing.")
        self.history = defaultdict(list)

    @staticmethod
    def _download(filename, model_url):
        if not model_url:
            return filename
        # This is a drity hack to avoid problems with ephemeral file systems
        return Mega().download_url(model_url, os.path.dirname(filename))

    def reply(self, update, context):
        uid = update.message.from_user.id
        self.history[uid].append(update.message.text.lower())

        error_answer = heuristics(update, context, self.history[uid])
        if error_answer is not None:
            return error_answer

        if self.model is None:
            return env("MESSAGE_DEFAULT")

        model = markovify.combine([
            self.model,
            markovify.Text(". ".join(self.history[uid]))
        ], weights=[1., 2.0])

        message = None
        while not message:
            message = model.make_sentence()
        return message
