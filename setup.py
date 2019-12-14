from setuptools import setup, find_packages

setup(
    name="nlg-playground",
    version="0.0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'train=model.train:main',
        ],
    },
)
