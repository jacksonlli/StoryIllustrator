from nltk.tokenize import sent_tokenize
import spacy


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
            sentences += sent_tokenize(sub_text)
        sentences = self._tokenize_subsentences(sentences)
        return sentences

    def _split_sentence(self, token, tokenization_length=20):
        doc = self.nlp(token)
        if len(doc) >= tokenization_length:
            subject_found = False
            split_indexes = []
            split_candidate = None
            for i, sub_tok in enumerate(doc):
                if sub_tok.dep_ in ["punct"]:  # "cc", 
                    split_candidate = i
                elif sub_tok.dep_ == "nsubj":
                    if subject_found and split_candidate:
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

    def _tokenize_subsentences(self, sentences):
        """
        Split sentences into sub sentences when possible
        """
        if isinstance(sentences, str):
            tokens = sent_tokenize(sentences)
        else:
            tokens = sentences
        new_tokens = []
        for token in tokens:
            token = token.replace('\n', '')
            new_tokens += self._split_sentence(token)
        tokens = new_tokens
        return tokens
