from environs import Env

env = Env()
env.read_env()


class Config:
    def __init__(self):
        env = Env()
        env.read_env()

        self.token = env("TOKEN")
        self.model_name = env.str("MODEL")
        self.message_start = env.str("MESSAGE_START")
        self.message_help = env.str("MESSAGE_HELP")
        self.message_version = env.str("MESSAGE_VERSION")
        self.message_about = env.str("MESSAGE_ABOUT")
        self.port = env.int("PORT", 5050)
        self.webhook = env.str("WEBHOOK_URL", None)
        if self.webhook is not None:
            self.webhook = f"{self.webhook}/{self.token}"


config = Config()
