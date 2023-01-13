from nltk.tokenize import sent_tokenize
import spacy
import re


class Screenplay:
    def __init__(self, text, title=None):
        if text[-4:] == ".txt":
            with open(text, "r", encoding="utf-8-sig") as t:
                text = t.read()
        if title:
            if title[-4:] == ".txt":
                with open(title, "r", encoding="utf-8-sig") as t:
                    title = t.read()
        self.text = text
        self.title = title
        self.full_text = self.title + ". " + self.text if self.title else self.text
        self._sentences = None
        self._illustration_sentences = None
        self._narration_sentences = None
        self.nlp = spacy.load("en_core_web_sm")

    @property
    def sentences(self):
        if not self._sentences:
            self._sentences = self.tokenize_sentences()
            if self.title:
                self._sentences = [self.title] + self._sentences
        return self._sentences

    @sentences.setter
    def sentences(self, values):
        if isinstance(values, list):
            self._sentences = values
        else:
            raise Exception(
                f"sentences expect a list of string, but got {type(values)}"
            )

    @property
    def illustration_sentences(self):
        if not self._illustration_sentences:
            self._illustration_sentences = self.sentences
        return self._illustration_sentences

    @sentences.setter
    def illustration_sentences(self, values):
        if isinstance(values, list):
            self._illustration_sentences = values
        else:
            raise Exception(
                f"sentences expect a list of string, but got {type(values)}"
            )

    @property
    def narration_sentences(self):
        if not self._narration_sentences:
            self._narration_sentences = re.sub(r'\\?\[SET:.*?\\?\]\n?', "", self.sentences)
        return self._narration_sentences

    @sentences.setter
    def narration_sentences(self, values):
        if isinstance(values, list):
            self._narration_sentences = values
        else:
            raise Exception(
                f"sentences expect a list of string, but got {type(values)}"
            )

    def tokenize_sentences(self):
        """
        Returns: List of strings
        """
        text = self.text.replace("“", '"').replace("”", '"')
        sentences = []
        split_delimiters = ["; ", "| " "\n"]
        for delim in split_delimiters:
            text = text.replace(delim, "|")
        for sub_text in text.split("|"):
            sub_text = re.sub(r'([!.?])"(\W[a-z])', r'\1temp"\2', sub_text)
            sub_text_sentences = sent_tokenize(sub_text)
            for sentence in sub_text_sentences:
                sentence = re.sub(r'([!.?])temp"(\W[a-z])', r'\1"\2', sentence)
                sentence = sentence.replace('\n', '')
                sub_sentences = self._split_sentence(sentence)
                sentences += sub_sentences
        return sentences

    def _split_sentence(self, token, tokenization_length=20):
        doc = self.nlp(token)
        if len(doc) >= tokenization_length:
            subject_found = False
            split_indexes = []
            split_candidate = None
            skip_zone = False

            for i, sub_tok in enumerate(doc):
                if str(sub_tok) in ['"', '[', ']']:
                    skip_zone = not skip_zone
                elif sub_tok.dep_ in ["punct"]:  # "cc", 
                    split_candidate = i
                elif sub_tok.dep_ == "nsubj" and not skip_zone:
                    if subject_found and split_candidate:
                        if not split_indexes or split_indexes[-1]!=split_candidate:
                            # split by punct, or cc
                            split_indexes.append(split_candidate)
                    subject_found = True
            split_indexes.append(len(token))
            splits = []
            for i in range(len(split_indexes)):
                splits.append(
                    str(doc[(split_indexes[i - 1] if i > 0 else -1) + 1 : split_indexes[i]])
                )
        else:
            splits = [token]

        return splits
