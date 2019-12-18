import pytest
from model.train import TextVectorizer


@pytest.fixture
def data():
    return [
        "All work and no play",
        "makes Jack a dull boy",
    ]


def test_text_transformation(data):
    lines = [line.split() for line in data]
    words = [word.lower() for line in lines for word in line]
    assert len(TextVectorizer().fit_transform(words)) == 10
