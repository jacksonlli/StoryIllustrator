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
        self.full_text = self.title + ". " + self.text if self.title else self.text
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
        text = self.text.replace("“", '"').replace("”", '"')
        sentences = []
        split_delimiters = ["; ", "| " "\n"]
        for delim in split_delimiters:
            text = text.replace(delim, "|")
        for sub_text in text.split("|"):
            sentences += sent_tokenize(sub_text)
        return sentences
