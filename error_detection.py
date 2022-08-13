import pandas as pd
import progressbar
import json

from trie import Trie, Item


class ErrorDetector:
    def __init__(self):
        self.sentences = list()
        self.nuclei = Trie()
        self.variation_nuclei = list()
        self.nil = Trie()
        self.found = 0

    def analyze_nil(self):
        """
        iterates through all the nuclei previously collected in analyze_sentences()
        and searches for variation nuclei among the NIL items
        """
        with progressbar.ProgressBar(max_value=len(self.nuclei)) as bar:
            count = 0
            for word1, level2 in self.nuclei.items():
                count += 1
                bar.update(count)
                for word2, items in level2.items():
                    for item in items:
                        nil_items = self.nil.find_pairs(word1, word2)
                        for nil_item in nil_items:
                            self.apply_nil_internal_context_heuristics(item, nil_item)

    def analyze_sentences(self):
        """
        main loop
        calls other functions to retrieve nuclei, search for variation nuclei and collect the NIL items
        """

        # init progressbar
        with progressbar.ProgressBar(max_value=len(self.sentences)//20) as bar:
            for i in range(len(self.sentences)//20):
                bar.update(i)
                sentence = self.sentences[i]

                # go through each word in the sentence
                for item in sentence:
                    if item[3] == 'PUNCT':
                        continue
                    self.collect_dependency_pair(sentence, item, i)
                    self.collect_nil_items(sentence, item, i)

    def apply_nil_internal_context_heuristics(self, item1: Item, item2: Item):
        """checks whether the two nuclei have the same internal context"""

        def get_internal_context(item: Item):
            """helper method """
            internal_context = list()
            sentence = self.sentences[item.sentence]
            for i in range(item.word1, item.word2 - 1):
                line = sentence[i]
                if line[3] == 'PUNCT':
                    continue
                internal_context.append(line[1])
            return internal_context

        context1 = get_internal_context(item1)
        context2 = get_internal_context(item2)

        if context1 == context2:
            if context1:
                self.variation_nuclei.append((item1, item2))

    def apply_non_fringe_heuristic(self, item1: Item, item2: Item):
        """compares the surrounding words of the two nucleus items"""

        def get_surrounding(item: Item):
            """helper method"""
            sentence = self.sentences[item.sentence]
            l1, r1, l2, r2 = "", "", "", ""

            if item.word1 > 1:
                l1_item = sentence[item.word1 - 2]
                if l1_item[3] == 'PUNCT':
                    if item.word1 > 2:
                        l1_item = sentence[item.word1 - 3]
                l1 = l1_item[1]

            r1_item = sentence[item.word1]
            if r1_item[3] == 'PUNCT':
                r1_item = sentence[item.word1 + 1]
            r1 = r1_item[1]

            l2_item = sentence[item.word2 - 2]
            if l2_item[3] == 'PUNCT':
                l2_item = sentence[item.word2 - 3]
            l2 = l2_item[1]

            if item.word2 < len(sentence) - 1:
                r2_item = sentence[item.word2]
                if r2_item[3] == 'PUNCT':
                    if item.word2 < len(sentence) - 2:
                        r2_item = sentence[item.word2 + 1]
                r2 = r2_item[1]

            return [l1, r1, l2, r2]

        context1 = get_surrounding(item1)
        context2 = get_surrounding(item2)

        if context1 == context2:
            self.variation_nuclei.append((item1, item2))

    def collect_dependency_pair(self, sentence: list, item: list, sentence_id: int):
        """creates the dependency pair of the item in the sentence
        & checks for variation nuclei within the already stored nuclei"""

        # retrieve the information from the current item
        word_id = int(item[0])
        word = item[1]
        head_id = int(item[6])
        label = item[7]

        # create the dependency pair regarding directedness
        head = sentence[head_id - 1][1]
        if head_id == 0:
            label = 'root-L'
            vn = self.nuclei.add_item('root', word, sentence_id, 0, word_id, label)
        elif head_id > word_id:
            label = label + '-R'
            vn = self.nuclei.add_item(word, head, sentence_id, word_id, head_id, label)
        elif head_id < word_id:
            label = label + '-L'
            vn = self.nuclei.add_item(head, word, sentence_id, head_id, word_id, label)
        else:
            return

        if vn:
            self.apply_non_fringe_heuristic(vn[0], vn[1])

    def collect_nil_items(self, sentence: list, item: list, sentence_id: int):
        """iterates through the sentence and fills up the trie structure
        with every NIL item regarding the specified item"""

        # retrieve the information from the current item
        word_id = int(item[0])
        word = item[1]
        head_id = int(item[6])

        # search the other items in the sentence
        for i in range(word_id, len(sentence)):
            other_item = sentence[i]

            if other_item[3] == 'PUNCT':
                continue
            other_word = other_item[1]
            other_word_id = int(other_item[0])
            other_head_id = int(other_item[6])

            # the two items must not have a dependency relation
            if head_id != other_word_id and other_head_id != word_id:
                self.nil.add_item(word, other_word, sentence_id, word_id, other_word_id)

    def detect_errors(self, filename: str):
        """ 'main' method to use the functions in this class"""

        # clear all class variables
        self.sentences.clear()
        self.nuclei.clear()
        self.variation_nuclei.clear()
        self.nil.clear()

        print("Read data...")
        self.read_data(filename)
        print("Done.")

        print("Start analysis...")
        self.analyze_sentences()
        print("\n\n")
        self.pretty_print_variation_nuclei()

        print("Analyzing NIL items...")
        self.analyze_nil()

        print("\n\n")
        self.pretty_print_variation_nuclei()
        # self.save_variation_nuclei()
        # self.load_variation_nuclei()

    def load_variation_nuclei(self):
        """loads the "raw" variation nuclei (without heuristics) from a json file"""
        self.variation_nuclei.clear()
        with open("data/variationNuclei.json", "r") as fp:
            variation_nuclei = json.load(fp)

        for vn in variation_nuclei:
            item1 = vn[0]
            item2 = vn[1]
            cur_item1 = Item(item1[0], item1[1], item1[2], item1[3])
            cur_item2 = Item(item2[0], item2[1], item2[2], item2[3])
            self.variation_nuclei.append((cur_item1, cur_item2))

    def pretty_print_variation_nuclei(self) -> None:
        """
        prints the variation nuclei as a dataframe
        """
        print("I found {} variation nuclei. Here are the first 20: \n".format(len(self.variation_nuclei)))
        df = pd.DataFrame(self.variation_nuclei[:20], columns=["pair1", "pair2"])
        # print(df)

    def read_data(self, filename: str) -> None:
        """
        reads in a text file in CONLL-U format
        :param filename: path to the file to read
        """
        with open(filename, 'r', encoding='utf8') as f:
            f.readline()  # ignore the 'newdoc' tag
            line = f.readline()
            sentence = list()
            while line:
                # blank line indicates a new sentence
                if line == '\n':
                    self.sentences.append(sentence)
                    sentence = list()
                else:

                    # prepare & filter out the lines
                    line = line.split('\t')
                    if line[0].startswith('#') or '-' in line[0]:
                        pass
                    else:
                        sentence.append(line)
                line = f.readline()
            if sentence:
                self.sentences.append(sentence)

    def save_variation_nuclei(self):
        """saves the "raw" variation nuclei (without heuristics) into a json file"""

        variation_nuclei = list()
        for vn in self.variation_nuclei:
            temp = vn[0]
            item1 = temp.to_list()
            item2 = vn[1].to_list()
            variation_nuclei.append((item1, item2))

        with open("data/variationNuclei.json", "w") as fp:
            json.dump(variation_nuclei, fp, indent=4)


if __name__ == '__main__':
    ed = ErrorDetector()
    fn = 'data/TuebaDZUpdated.txt'
    ed.detect_errors(fn)
