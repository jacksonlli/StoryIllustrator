from setuptools import setup, find_packages

setup(
    name="story_illustrator",
    version="1.0.1",
    description="",
    packages=find_packages(),
    install_requires=[
        "torch",
        "numpy",
        "tqdm",
        "nltk",
        "srt",
        "moviepy",
        "spacy==2.1",
        "pattern",
        "omegaconf",
    ],
)
