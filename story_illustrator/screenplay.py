from nltk.tokenize import sent_tokenize


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
        self._sentences = None

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
        self.sentences = sent_tokenize(self.text)
        return self.sentences
