class Item:
    """represents an item in CONLL-U format
    holds the location indices and a label (except for NIL items)"""
    def __init__(self, sentence: int, word1: int, word2: int, label=None):
        self.sentence = sentence
        self.word1 = word1
        self.word2 = word2
        if isinstance(label, set):
            self.label = set()
            for la in label:
                self.label.add(la)
        else:
            self.label = {label} if label else None

    def get_label(self):
        """returns the label string if there is only one, else the set"""
        if len(self.label) == 1:
            (label,) = self.label
            return label
        else:
            return self.label

    def get_label_str(self):
        """extract the label string out of the class variable"""
        if not self.label:
            return "NIL"
        elif len(self.label) == 1:
            (label,) = self.label
            return label

    def head(self):
        """returns the word which is the head of the pair"""
        if self.label:

            # this will ofc only iterate once, but its more convenient this way
            for label in self.label:
                if label.endswith('L'):
                    return self.word1
                else:
                    return self.word2
        return None

    def overlaps_with(self, other) -> bool:
        """checks for a given item, whether there is an overlap"""
        if self.sentence == other.sentence:
            if self.head() == other.head():
                return True
            return False
        return False

    def to_list(self, word1: str, word2: str):
        """returns a list version of itself (for json storing purposes)"""
        return[self.sentence, [self.word1, word1], [self.word2, word2], [la for la in self.label] if self.label else None]

    def __str__(self):
        if self.label:
            label = ""
            for la in self.label:
                label = label + la + ", "
            label = label[:-2]
        else:
            label = "NIL"
        return "{} - {} - {} : {}".format(self.sentence + 1, self.word1, self.word2, label)

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
        variation_nucleus = list()
        item = Item(sentence_id, word1_id, word2_id, label)

        if word1 in self:
            level2 = self[word1]
            if word2 in level2:

                # NIL trie does not have to do this
                add_it = True
                if label:
                    for other_item in level2[word2]:

                        # handle overlap
                        if item.overlaps_with(other_item):
                            other_item.label.add(label)
                            add_it = False
                        else:
                            # check for variation nuclei
                            if label not in other_item.label:
                                variation_nucleus.append((item, other_item))

                if add_it:
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
