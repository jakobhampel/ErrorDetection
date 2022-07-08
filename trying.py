import sys
import pandas as pd


def pretty_print_pairs(dependency_pairs: list) -> None:
    """
    prints the pairs-table as a dataframe
    :param dependency_pairs: list of dependency pairs
    :return: None
    """
    df = pd.DataFrame(dependency_pairs, columns=['word1', 'word2', 'label'])
    print(df)


def read_data(filename: str) -> list:
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
        if sentence:
            sentences.append(sentence)

    return sentences


def retrieve_all_dependency_pairs(sentences: list) -> list:
    """
    helper method to call the retrieve_dependency_pairs method several times
    :param sentences: a list of lists; each list represents a full sentence in CONLL-U format
    :return:a list of tuples containing the pair and the label
    """
    # TODO: store them as a trie
    dependency_pairs = list()
    for sentence in sentences:
        sentence_pairs = retrieve_dependency_pairs(sentence)
        dependency_pairs += sentence_pairs
    return dependency_pairs


def retrieve_dependency_pairs(sentence: list) -> list:
    """
    creates the dependency pairs
    :param sentence: a list comprising a full sentence in CONLL-U format
    :return: a list of tuples containing the pair and the label
    """
    sentence_pairs = list()
    sentence = [item for item in sentence if not item.startswith('#')]  # ignore the sent_id and text info

    for item in sentence:
        item = item.split('\t')

        # retrieve the information from the current item
        word_id = int(item[0])
        word = item[1]
        head_id = int(item[6])
        label = item[7]

        # based on the head_id, retrieve the head in the sentence
        head = sentence[head_id - 1].split('\t')[1]

        # assign the dependency label, including directedness
        if head_id == 0:
            sentence_pairs.append(('root', word, 'root-L'))
        elif head_id > word_id:
            sentence_pairs.append((word, head, label + '-R'))
        elif head_id < word_id:
            sentence_pairs.append((head, word, label + '-L'))
        else:
            sys.exit(1)

    return sentence_pairs


if __name__ == '__main__':
    fn = 'data/TuebaDZ_superShortVersion.txt'
    data = read_data(fn)
    dp = retrieve_all_dependency_pairs(data)
    pretty_print_pairs(dp)
