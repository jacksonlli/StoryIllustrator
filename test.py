import spacy
from pattern.en import conjugate


def _split_sentence(nlp, token):
    doc = nlp(token)
    subject_found = False
    split_indexes = []
    split_candidate = None
    for i, sub_tok in enumerate(doc):
        if sub_tok.dep_ in ["cc", "punct"]:
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
            doc[(split_indexes[i - 1] if i > 0 else -1) + 1 : split_indexes[i]]
        )
    return splits


nlp = spacy.load("en_core_web_sm")
sent = (
    "The cat went into the store, he browsed the catalogue and he bought a large fish."
)


def _key_word_redudancy(nlp, token):
    doc = nlp(token)
    key_words = []
    for sub_tok in doc:
        if sub_tok.pos_ in ["PROPN", "NOUN"]:
            key_words.append(sub_tok.text)
        elif sub_tok.pos_ == "VERB":
            base_verb = sub_tok.lemma_
            for i in range(2):
                try:
                    conjugated_verb = conjugate(base_verb, "part")
                    break
                except Exception:
                    conjugated_verb = base_verb
            key_words.append(conjugated_verb)
    return " ".join(key_words)


# _split_sentence(nlp, 'The cat went into the store, he browsed the catalogue and he bought a large fish.')\
print(
    _key_word_redudancy(
        nlp,
        "The cat went into the store, he browsed the catalogue and he bought a large fish.",
    )
)
