import sys


class NucleiFinder:
    """class to read in a dependency treebank in CONLL-U format and to compute variation nuclei in the treebank"""

    def __init__(self):
        self.nuclei = dict()


def read_data(filename: str):
    """
    reads in a text file in CONLL-U format
    :param filename: path to the file to read
    :return: a list of lists, representing the sentence blocks in the text file
    """
    sentences = list()
    with open(filename, 'r', encoding='utf8') as f:
        f.readline()  # ignore the 'newdoc' tag
        line = f.readline()
        sentence = list()
        while line:
            # blank line indicates a new sentence
            if line == '\n':
                sentences.append(sentence)
                sentence = list()
            else:
                sentence.append(line)
            line = f.readline()

    return sentences


def retrieve_dependency_pairs(sentence: list):
    """
    creates the dependency pairs
    :param sentence: a list comprising a full sentence in CONLL-U format
    :return: a dictionary with KEYS: tuples of two words and VALUES: the corresponding dependency labels
    """
    dependency_pairs = dict()
    sentence = [item for item in sentence if not item.startswith('#')]  # ignore the sent_id and text info

    for item in sentence:
        item = item.split('\t')
        word_id = int(item[0])
        word = item[1]
        head_id = int(item[6])
        head = sentence[head_id - 1].split('\t')[1]
        label = item[7]

        if head_id == 0:
            dependency_pairs[('root', word)] = 'root-L'
        elif head_id > word_id:
            dependency_pairs[(word, head)] = label + '-R'
        elif head_id < word_id:
            dependency_pairs[(head, word)] = label + '-L'
        else:
            sys.exit(1)

    return dependency_pairs


if __name__ == '__main__':
    fn = 'data/TuebaDZ_superShortVersion.txt'
    data = read_data(fn)
    dp = retrieve_dependency_pairs(data[0])

    for k, v in dp.items():
        print(k[0] + ' ' + k[1] + '\t\t\t' + v)
