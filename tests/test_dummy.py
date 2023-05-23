import os
from unittest.mock import patch


@patch.dict(
    os.environ,
    {
        "TOKEN": "FakeToken",
        "ADMIN_IDS": "1,2",
        "THANKS_STICKERS": "1",
        "MESSAGE_THANKS": "Thanks",
        "MESSAGE_START": "Hey",
        "MESSAGE_HELP": "Help",
    },
)
def test_imports():
    from bot.main import main  # noqa
