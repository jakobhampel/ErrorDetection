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

    def __eq__(self, other):
        return (self.sentence == other.sentence and
                self.word1 == other.word1 and
                self.word2 == other.word2 and
                self.label == other.label)


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

                # NIL trie does not have to do this
                if label:
                    for other_item in level2[word2]:
                        """head_id = word1_id if label.endswith('L') else word2_id
                        # go through the set of overlapping labels
                        if isinstance(other_item, set):
                            variation = True
                            for overlap in other_item:
                                if overlap.sentence == sentence_id and overlap.head() == head_id:
                                    other_item.add(item)
                                    variation = False
                                    break
                                elif overlap.label == label:
                                    variation = False
                            if variation:
                                variation_nucleus = (item, other_item)
                        else:
                            # check for overlap
                            if other_item.sentence == sentence_id and other_item.head() == head_id:
                                level2[word2].remove(other_item)
                                overlapping_items = {other_item, item}
                                level2[word2].append(overlapping_items)"""

                        # check for variation nuclei
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
