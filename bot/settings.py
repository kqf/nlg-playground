from environs import Env

env = Env()
env.read_env()

token = env("TOKEN")
model_name = env.str("MODEL")
model_url = env.str("MODEL_URL", "")
message_start = env.str("MESSAGE_START")
message_help = env.str("MESSAGE_HELP")
message_version = env.str("MESSAGE_VERSION")
message_about = env.str("MESSAGE_ABOUT")
port = env.int("PORT", 5050)
webhook = env.str("WEBHOOK_URL", None)
if webhook is not None:
    webhook = f"{webhook}/{token}"
