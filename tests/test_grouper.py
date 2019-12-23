import pytest
import pandas as pd
from model.dataset import dt_groups


@pytest.fixture
def date_col():
    return "date"


@pytest.fixture
def data(date_col):
    df = pd.DataFrame(
        {date_col: [
            "2017-09-21 07:00:00",
            "2017-09-21 08:00:00",
            "2017-09-21 08:29:00",
            "2017-09-21 10:00:00",
            "2017-09-21 10:15:00",
            "2017-09-21 12:35:00",
            "2017-09-21 12:40:00",
            "2017-09-21 13:04:00",
        ]})
    df[date_col] = df[date_col].astype("datetime64")
    return df.sort_values(date_col)


def test_grouper(data, date_col):
    groupped = data.groupby(dt_groups(data, date_col))[date_col].apply(list)
    assert len(groupped) == 4
