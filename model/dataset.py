import click
import json
import pandas as pd
from environs import Env


def read_raw_export(filename, target_name):
    with open(filename) as f:
        data = json.load(f)

    contants = [x["name"] for x in data["frequent_contacts"]["list"]]
    idx = contants.index(target_name)
    return pd.DataFrame(data["chats"]["list"][idx]["messages"])


def dt_groups(df, col, interval='30m'):
    na = pd.Timedelta(seconds=0)
    return (df[col].diff().fillna(na) >= interval).cumsum()


@click.command()
@click.option('--ifile', type=str, required=True)
@click.option('--ofile', type=str, required=True)
def main(ifile, ofile):
    env = Env()
    env.read_env()
    target_name = env("TARGET_NAME")
    df = read_raw_export(ifile, target_name)

    df = df[df["from"] == target_name].reset_index()
    df["text"] = df["text"].str.replace('\n', ' ')
    df = df[df["text"].astype(bool)]
    df = df[~df["text"].str.contains(r"\[{'").astype(bool)]
    df["text"] = df["text"].str.strip()
    # df["date"] = df["date"].astype("datetime64")
    # messages = df.groupby(dt_groups(df, "date"))["text"].apply(" ".join)
    messages = df["text"]
    print(messages.head(5))
    messages.to_csv(ofile, header=False, index=False, sep="@")


if __name__ == '__main__':
    main()
