from nltk.tokenize import sent_tokenize


class Screenplay:
    def __init__(self, text):
        if text[-4:] == ".txt":
            with open(text, "r", encoding="utf-8-sig") as t:
                text = t.read()
        self.text = text
        self._sentences = None

    @property
    def sentences(self):
        return self._sentences if self._sentences else self.tokenize_sentences()

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
        self.sentences = sent_tokenize(self.text)
        return self.sentences
