import json
import pandas as pd
from environs import Env

env = Env()
env.read_env()
TARGET_NAME = env("TARGET_NAME")


def target_idx(data):
    contants = [x["name"] for x in data["frequent_contacts"]["list"]]
    return contants.index(TARGET_NAME)


def main():
    with open("data/result.json") as f:
        data = json.load(f)

    idx = target_idx(data)
    df = pd.DataFrame(data["chats"]["list"][idx]["messages"])
    df = df[df["from"] == TARGET_NAME].reset_index()
    df["text"] = df["text"].str.replace('\n', ' ')
    df = df[df["text"].astype(bool)]
    df = df[~df["text"].str.contains(r"\[{'").astype(bool)]
    df["text"] = df["text"].str.strip()
    print(df["text"].head(5))
    df["text"].to_csv("data/input.txt", header=False, index=False, sep="@")
    # from IPython import embed; embed()


if __name__ == '__main__':
    main()
