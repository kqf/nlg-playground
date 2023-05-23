from setuptools import find_packages, setup

setup(
    name="nlg-playground",
    version="0.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "nlg-train=model.main:train",
            "nlg-generate=model.main:generate",
            "nlg-dialogue=model.main:dialogue",
            "nlg-dataset=model.dataset:main",
            "nlg-raw-data=model.dataset:download",
            "oleg=bot.run:main",
        ],
    },
)
