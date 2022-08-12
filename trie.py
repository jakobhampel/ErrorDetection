class Item:
    """represents an item in CONLL-U format
    holds the location indices and a label (except for NIL items)"""
    def __init__(self, sentence: int, word1: int, word2: int, label: str = None):
        self.sentence = sentence
        self.word1 = word1
        self.word2 = word2
        self.label = label

    def head(self):
        if self.label:
            if self.label.endswith('L'):
                return self.word1
            else:
                return self.word2
        else:
            return None

    def overlaps_with(self, other) -> bool:
        if self.sentence == other.sentence:
            if self.head() == other.head():
                return True
            return False
        return False

    def to_list(self):
        """returns a list version of itself (for json storing purposes)"""
        return[self.sentence, self.word1, self.word2, self.label]

    def __str__(self):
        return "{} - {} - {} : {}".format(self.sentence, self.word1, self.word2, self.label if self.label else "NIL")


class Trie(dict):
    """implementation of a dictionary storing word pairs trie-wise"""
    def __init__(self):
        super(Trie, self).__init__()

    def add_item(self, word1: str, word2: str, sentence_id: int, word1_id: int, word2_id: int, label: str = None):
        """ adds an item to the trie structure, returns a variation nucleus, if detected"""
        variation_nucleus = tuple()
        item = Item(sentence_id, word1_id, word2_id, label)
        if word1 in self:
            level2 = self[word1]
            if word2 in level2:
                for other_item in level2[word2]:
                    # TODO: implement overlap handling
                    if item.label != other_item.label:
                        variation_nucleus = (item, other_item)
                level2[word2].append(item)
            else:
                level2[word2] = [item]
        else:
            level2 = dict()
            level2[word2] = [item]
            self[word1] = level2
        return variation_nucleus

    def find_pairs(self, word1: str, word2: str):
        """ searches for a word pair in the trie and returns the corresponding items"""
        items = []
        if word1 in self:
            level2 = self[word1]
            if word2 in level2:
                items = level2[word2]
        return items

    def pretty_print(self):
        """ pretty prints the two levels of the trie"""
        for key, values in self.items():
            for value, items in values.items():
                for item in items:
                    print(key + "\t" + value + "\t" + str(item))
