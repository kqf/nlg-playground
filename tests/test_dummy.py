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
        "MODEL": "123",
        "MESSAGE_VERSION": "123",
        "MESSAGE_ABOUT": "msg",
    },
)
def test_imports():
    from bot.main import main  # noqa
