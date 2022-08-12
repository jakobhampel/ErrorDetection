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
                            self.variation_nuclei.append((item, nil_item))

    def analyze_sentences(self):
        """
        main loop
        calls other functions to retrieve nuclei, search for variation nuclei and collect the NIL items
        """

        # init progressbar
        with progressbar.ProgressBar(max_value=len(self.sentences)//20) as bar:
            for i in range(len(self.sentences)//20):
                bar.update(i)

                # go through each word in the sentence
                # skip sent_id, text info, punctuation & merged words
                sentence = [item for item in self.sentences[i] if not item.startswith('#')]
                for item in sentence:
                    item = item.split('\t')
                    if '-' in item[0] or item[3] == 'PUNCT':
                        continue

                    self.collect_dependency_pair(sentence, item, i+1)
                    self.collect_nil_items(sentence, item, i+1)

    def apply_nil_internal_context_heuristics(self, item1: Item, item2: Item):
        self.found += 1

    def collect_dependency_pair(self, sentence: list, item: list, sentence_id: int):
        """creates the dependency pair of the item in the sentence
        & checks for variation nuclei within the already stored nuclei"""

        # retrieve the information from the current item
        word_id = int(item[0])
        word = item[1]
        head_id = int(item[6])
        label = item[7]

        # create the dependency pair regarding directedness
        head = sentence[head_id - 1].split('\t')[1]
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
            self.variation_nuclei.append(vn)

    def collect_nil_items(self, sentence: list, item: list, sentence_id: int):
        """iterates through the sentence and fills up the trie structure
        with every NIL item regarding the specified item"""

        # retrieve the information from the current item
        word_id = int(item[0])
        word = item[1]
        head_id = int(item[6])

        # search the other items in the sentence
        for i in range(word_id, len(sentence)):
            other_item = sentence[i].split('\t')
            if '-' in other_item[0] or other_item[3] == 'PUNCT':
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

        print("Analyzing NIL items...")
        self.analyze_nil()

        print("\n\n")
        self.pretty_print_variation_nuclei()
        self.save_variation_nuclei()
        self.load_variation_nuclei()
        self.pretty_print_variation_nuclei()

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
        print(df)

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
