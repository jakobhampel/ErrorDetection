import pandas as pd
import progressbar

from trie import Trie


class ErrorDetector:
    def __init__(self):
        self.sentences = list()
        self.nuclei = dict()
        self.variation_nuclei = list()
        self.nil = dict()

    def apply_heuristics(self):
        pass

    def compute_variation_nuclei(self, cut: int = 0):
        """
        searches for nuclei with more than one label
        :param cut: limits the search range within the nuclei list; if 0, use the whole list
        """
        if cut < 0 or cut > len(self.nuclei):
            print("Search range is invalid.")
            return
        elif cut:
            search_range = cut
        else:
            search_range = len(self.nuclei)

        with progressbar.ProgressBar(max_value=search_range) as bar:
            for i in range(search_range):
                bar.update(i)
                nucleus = self.nuclei[i]
                for j in range(i + 1, search_range):
                    candidate = self.nuclei[j]
                    if nucleus[0] == candidate[0] and nucleus[1] == candidate[1]:  # same word pair
                        if nucleus[2] != candidate[2]:  # different label
                            self.variation_nuclei.append([nucleus, candidate])

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

        print("Retrieve dependency pairs...")
        self.retrieve_dependency_pairs()
        print("Done.")
        """print("\n There are {} nuclei found in the file".format(str(len(self.nuclei))))
        cut = len(self.nuclei) // 100
        print("I will now analyze the first {} nuclei.".format(str(cut)))"""

        self.pretty_print_variation_nuclei()

    def pretty_print_pairs(self) -> None:
        """
        prints the nuclei as a dataframe
        """
        df = pd.DataFrame(self.nuclei[:100], columns=['word1', 'word2', 'label'])
        print(df)

    def pretty_print_variation_nuclei(self) -> None:
        """
        prints the variation nuclei as a dataframe
        """
        print("I found {} variation nuclei. Here are the first 20: \n".format(len(self.variation_nuclei)))
        df = pd.DataFrame(self.variation_nuclei[:20], columns=["word pair", "label 1", "label 2"])
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

    def retrieve_dependency_pairs(self, cut: int = 0) -> None:
        """
        creates the dependency pairs
        """

        if cut < 0 or cut > len(self.sentences):
            print("Search range is invalid.")
            return
        elif cut:
            search_range = cut
        else:
            search_range = len(self.sentences)

        with progressbar.ProgressBar(max_value=search_range) as bar:
            for i in range(search_range):
                bar.update(i)
                sentence = [item for item in self.sentences[i] if not item.startswith('#')]  # ignore the sent_id and text info

                for item in sentence:
                    item = item.split('\t')
                    if '-' in item[0] or item[3] == 'PUNCT':
                        # skip punctuation & the merged words, they are already handled in the CONLL-U format
                        continue

                    # retrieve the information from the current item
                    word_id = int(item[0])
                    word = item[1]
                    head_id = int(item[6])
                    label = item[7]

                    # based on the head_id, retrieve the head in the sentence
                    head = sentence[head_id - 1].split('\t')[1]

                    # assign the dependency label, including directedness
                    # TODO: append sentence info to value (instead of 0)
                    if head_id == 0:
                        key = ('root', word)
                        value = ('root-L', 0)
                    elif head_id > word_id:
                        key = (word, head)
                        value = (label + '-R', 0)
                    elif head_id < word_id:
                        key = (head, word)
                        value = (label + '-L', 0)
                    else:
                        return

                    # check if key exists
                    if key in self.nuclei:
                        other_value = self.nuclei[key]

                        # check for variation nuclei and create new value content
                        for v in other_value:
                            if value[0] != v[0]:
                                self.variation_nuclei.append([key, value, v])
                        other_value.append(value)
                        value = other_value
                    else:
                        value = [value]

                    # append the new dependency pair to the nuclei dictionary
                    self.nuclei[key] = value


if __name__ == '__main__':
    ed = ErrorDetector()
    fn = 'data/TuebaDzUpdated.txt'
    ed.detect_errors(fn)
