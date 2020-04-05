import click
import json
import tqdm
import pandas as pd

from environs import Env
from telethon.sync import TelegramClient


env = Env()
env.read_env()

API_ID = env("API_ID")
API_HASH = env("API_HASH")
TARGET_NAME = env("TARGET_NAME")
TARGET_UNAME = env("TARGET_UNAME")
# Limit the query, otherwise it will take ages
MESSAGE_LIMIT = env.int("MESSAGE_LIMIT")


def payload(client, message):
    return {
        "from": client.get_entity(message.sender_id).first_name,
        "date": str(message.date),
        "text": message.text
    }


@click.command()
@click.option('--ofile', type=str, required=True)
def download(ofile):
    messages = []
    with TelegramClient("download", API_ID, API_HASH) as client:
        pool = tqdm.tqdm(
            client.iter_messages(TARGET_UNAME, limit=MESSAGE_LIMIT),
            # total=client.get_messages(TARGET_UNAME)[0].id
            total=MESSAGE_LIMIT
        )
        for msg in pool:
            messages.append(payload(client, msg))

    with open(ofile, "w") as f:
        json.dump(messages, f)


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
    df = pd.read_json(ifile)

    df = df[df["from"] == TARGET_NAME].reset_index()
    df["text"] = df["text"].str.replace('\n', ' ')
    df = df[df["text"].astype(bool)]
    df = df[~df["text"].str.contains(r"\[{'").astype(bool)]
    df["text"] = df["text"].str.strip()
    # df["date"] = df["date"].astype("datetime64")
    # messages = df.groupby(dt_groups(df, "date"))["text"].apply(" ".join)
    messages = df["text"]
    print(messages.head(5))
    messages.to_csv(ofile, header=False, index=False, sep="@")
