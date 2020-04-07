import logging
import os
import json
import markovify

from mega import Mega
from environs import Env

logger = logging.getLogger(__name__)

env = Env()
env.read_env()


class ReplyBot:
    def __init__(self, filename, model_url):
        self.model = None
        try:
            filename = self._download(filename, model_url)
            with open(filename, encoding='utf-8') as f:
                self.model = markovify.Text.from_json(json.load(f))
        except FileNotFoundError:
            logger.error(f"Model file {filename} is missing.")

    @staticmethod
    def _download(filename, model_url):
        if not model_url:
            return filename
        # This is a drity hack to avoid problems with ephemeral file systems
        return Mega().download_url(model_url, os.path.dirname(filename))

    def reply(self, context, user):
        if self.model is None:
            return env("MESSAGE_DEFAULT")

        message = None
        while not message:
            message = self.model.make_sentence()
        return message
