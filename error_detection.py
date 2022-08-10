import pandas as pd
import progressbar

from trie import Trie
from conllu_pair import DependencyPair


class ErrorDetector:
    def __init__(self):
        self.sentences = list()
        self.nuclei = dict()
        self.variation_nuclei = list()
        self.nil = dict()

    def add_nil(self, word1: str, word2: str, location: tuple):
        """adds a nil pair to the dictionary in a trie-like manner"""
        if word1 in self.nil:
            level2 = self.nil[word1]
            if word2 in level2:
                level2[word2].append(location)
            else:
                level2[word2] = [location]
        else:
            level2 = dict()
            level2[word2] = [location]
            self.nil[word1] = level2

    def analyze_sentences(self):
        """
        main loop
        calls other functions to retrieve nuclei, search for variation nuclei and collect the NIL items
        """

        # init progressbar
        with progressbar.ProgressBar(max_value=len(self.sentences)//2) as bar:
            for i in range(len(self.sentences)//2):
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
            key = ('root', word)
            dependency_pair = DependencyPair(key, 'root-L', sentence_id, 0, word_id)
        elif head_id > word_id:
            key = (word, head)
            dependency_pair = DependencyPair(key, label + '-R', sentence_id, word_id, head_id)
        elif head_id < word_id:
            key = (head, word)
            dependency_pair = DependencyPair(key, label + '-L', sentence_id, head_id, word_id)
        else:
            return

        # check if dependency pair already exists
        if key in self.nuclei:
            other_pairs = self.nuclei[key]

            # check for variation nuclei
            for pair in other_pairs:
                if pair.overlaps_with(dependency_pair):
                    continue
                if pair != dependency_pair:
                    self.variation_nuclei.append([dependency_pair, pair])

            # create value content
            value = other_pairs + [dependency_pair]
        else:
            value = [dependency_pair]

        # append the new dependency pair to the nuclei dictionary
        self.nuclei[key] = value

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
                location = (sentence_id, word_id, other_word_id)
                self.add_nil(word, other_word, location)

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
        print("There are {} distinct word pairs in the file".format(str(len(self.nuclei))))
        # self.pretty_print_pairs()
        self.pretty_print_variation_nuclei()

    def pretty_print_pairs(self) -> None:
        """
        prints the nuclei as a dataframe
        """
        for pairs in self.nuclei.values():
            for pair in pairs:
                print(pair)

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


if __name__ == '__main__':
    ed = ErrorDetector()
    fn = 'data/TuebaDZUpdated.txt'
    ed.detect_errors(fn)
