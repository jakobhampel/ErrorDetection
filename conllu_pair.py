class DependencyPair:
    """represents a dependency pair of two items in CONLL-U format"""

    def __init__(self, word_tuple: tuple, label: str, sentence_id: int, word1_id: int, word2_id: int):

        self.word1 = word_tuple[0]
        self.word2 = word_tuple[1]
        self.label = label

        self.sentence_id = sentence_id
        self.word1_id = word1_id
        self.word2_id = word2_id

    def head_id(self):
        """returns the head word"""
        if self.label.endswith("L"):
            return self.word1_id
        else:
            return self.word2_id

    def overlaps_with(self, other):
        if self.sentence_id == other.sentence_id:
            if self.head_id() == other.head_id():
                return True
            return False
        return False

    def __eq__(self, other):
        if (self.word1 == other.word1
                and self.word2 == other.word2
                and self.label == other.label):
            return True
        else:
            return False

    def __str__(self):
        return "{} - {} : {}".format(self.word1, self.word2, self.label)


class NILPair:
    """represents a pair of two items without a dependency label"""
    def __init__(self, sentence_id, word1_id, word2_id):
        self.sentence_id = sentence_id
        self.word1_id = word1_id
        self.word2_id = word2_id
