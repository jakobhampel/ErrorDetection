class DependencyPair:
    """represents a dependency pair of two items in CONLL-U format"""

    def __init__(self, word_tuple: tuple, label: str, sentence_id: int, word1_id: int, word2_id: int):

        self.word1 = word_tuple[0]
        self.word2 = word_tuple[1]
        self.label = label

        self.sentence_id = sentence_id
        self.word1_id = word1_id
        self.word2_id = word2_id

    def __eq__(self, other):
        if (self.word1 == other.word1
                and self.word2 == other.word2
                and self.label == other.label):
            return True
        else:
            return False

    def __str__(self):
        return "{} - {} : {}".format(self.word1, self.word2, self.label)
