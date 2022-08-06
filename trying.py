import pandas as pd
import progressbar


class ErrorDetector:
    def __init__(self):
        self.sentences = list()
        self.nuclei = list()
        self.variation_nuclei = list()
        self.nil = dict()

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
        print("\n There are {} nuclei found in the file".format(str(len(self.nuclei))))
        cut = len(self.nuclei) // 100
        print("I will now analyze the first {} nuclei.".format(str(cut)))

        self.compute_variation_nuclei(cut)
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
        df = pd.DataFrame(self.variation_nuclei[:20], columns=["variation1", "variation2"])
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

    def retrieve_dependency_pairs(self) -> None:
        """
        creates the dependency pairs
        """
        for sentence in self.sentences:
            sentence = [item for item in sentence if not item.startswith('#')]  # ignore the sent_id and text info

            for item in sentence:
                item = item.split('\t')
                if '-' in item[0]:
                    # skip the merged words, they are already handled in the CONLL-U format
                    continue

                # retrieve the information from the current item
                word_id = int(item[0])
                word = item[1]
                head_id = int(item[6])
                label = item[7]

                # based on the head_id, retrieve the head in the sentence
                head = sentence[head_id - 1].split('\t')[1]

                # assign the dependency label, including directedness
                if head_id == 0:
                    self.nuclei.append(('root', word, 'root-L'))
                elif head_id > word_id:
                    self.nuclei.append((word, head, label + '-R'))
                elif head_id < word_id:
                    self.nuclei.append((head, word, label + '-L'))


if __name__ == '__main__':
    ed = ErrorDetector()
    fn = 'data/TuebaDzUpdated.txt'
    ed.detect_errors(fn)
