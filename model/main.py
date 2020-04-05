import json
import click
import markovify

from datetime import datetime


@click.command()
@click.option('--output', '-o', default="artifacts/")
@click.option('--inputs', required=True)
def train(output, inputs):
    # Get raw text as string.
    with open(inputs) as f:
        text = f.read()

    # Build the model.
    model = markovify.NewlineText(text)

    # Save the model
    with open(output, "w", encoding='utf-8') as f:
        json.dump(model.to_json(), f, ensure_ascii=False, indent=4)
    print("Training has been finished")


@click.command()
@click.option('--num-lines', '-l', default=10, type=int)
@click.option('--num-words', '-w', default=10, type=int)
@click.option('--seed', type=int, default=datetime.now().microsecond)
@click.option('--method', '-m', default="hmm", type=str)
@click.option('--filename', type=str, required=True)
def generate(num_lines, num_words, seed, method, filename):
    with open(filename, encoding='utf-8') as f:
        model = markovify.Text.from_json(json.load(f))
    print(model.make_sentence())


@click.command()
@click.option('--filename', type=str, required=True)
def dialogue(filename):
    with open(filename, encoding='utf-8') as f:
        model = markovify.Text.from_json(json.load(f))
    for _ in range(5):
        print(model.make_sentence_with_start(input(), strict=False))
