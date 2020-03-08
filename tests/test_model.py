import pytest
from model.main import TextVectorizer


@pytest.fixture
def data():
    return [
        "All work and no play",
        "makes Jack a dull boy",
    ]


def test_text_transformation(data):
    lines = [list(line) for line in data]
    n_words = sum([len(line) for line in lines])
    assert len(TextVectorizer().fit_transform(lines)) == n_words
