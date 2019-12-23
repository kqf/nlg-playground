import json
import pandas as pd
from environs import Env


def target_idx(data, target_name):
    contants = [x["name"] for x in data["frequent_contacts"]["list"]]
    return contants.index(target_name)


def dt_groups(df, col, interval='30m'):
    na = pd.Timedelta(seconds=0)
    return (df[col].diff().fillna(na) >= interval).cumsum()


def main():
    env = Env()
    env.read_env()
    target_name = env("TARGET_NAME")

    with open("data/result.json") as f:
        data = json.load(f)

    idx = target_idx(data, target_name)
    df = pd.DataFrame(data["chats"]["list"][idx]["messages"])
    df = df[df["from"] == target_name].reset_index()
    df["text"] = df["text"].str.replace('\n', ' ')
    df = df[df["text"].astype(bool)]
    df = df[~df["text"].str.contains(r"\[{'").astype(bool)]
    df["text"] = df["text"].str.strip()
    print(df["text"].head(5))
    # from IPython import embed; embed()
    df["text"].to_csv("data/input.txt", header=False, index=False, sep="@")


if __name__ == '__main__':
    main()
