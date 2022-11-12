"""offers functions to post process json files of variation nuclei

NOTE: Some functions in this file may not work or do not follow proper coding conventions.
However, many of them were mainly used for testing purposes
and none of them contributes to the actual error detection process"""

import json
from trie import Item
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np


def read_vn(filename):
    """loads the variation nuclei from a json file"""
    result = list()
    with open(filename, "r") as fp:
        variation_nuclei = json.load(fp)
    for vn in variation_nuclei:
        i1 = vn[0]
        i2 = vn[1]

        item1 = Item(i1[0], i1[1][0], i1[2][0], set(i1[3]) if i1[3] else None)
        item2 = Item(i2[0], i2[1][0], i2[2][0], set(i2[3]) if i2[3] else None)
        word1, word2 = i1[1][1], i1[2][1]
        result.append([item1, item2, word1, word2])
    return result


def check_overlaps():
    """collects all items that participate in an overlap"""
    fn = "data/variationNuclei.json"
    vn = read_vn(fn)
    print(len(vn))
    result = list()
    for v in vn:
        item1 = v[0]
        if len(item1.label) > 1:
            result.append(v)
    convert_to_txt(result)


def collect_statistics(filename: str):
    """calls the other methods to get all statistical information
    prints out the results with semicolon-separator for easy copy-pasting it into a tabular version"""

    unique_sentence_ids = get_sentence_ids(filename)
    print("There are {} distinct sentences where variation nuclei were found.".format(str(len(unique_sentence_ids))))

    print("\n\nThese are the sentences that occurred most often: \n")
    for s in most_frequent_sentences(filename):
        print(str(s[0]) + ';' + str(s[1]))

    print("\n\nThese are the specific variation nuclei that occurred most often: \n")
    for vn in most_frequent_vn(filename):
        print(vn[0] + ';' + str(vn[1]))

    print("\n\nThese are the labels that occurred in the variation nuclei: \n")
    for label in get_label_statistics(filename):
        print(label[0] + ';' + str(label[1]))

    print("\n\nThese are the label pairs that occurred in the variation nuclei: \n")
    for pair in get_label_pair_statistics(filename):
        print(pair[0][0] + ';' + pair[0][1] + ';' + str(pair[1]))


def compare_results():
    version1 = ""
    version2 = ""

    vn1 = read_vn(version1)
    vn2 = read_vn(version2)

    result = list()
    for v in vn2:
        if v not in vn1:
            result.append(v)

    convert_to_txt(result)


def convert_to_txt(vn: list = None):
    """converts a json file to a txt lists, creates URLs for Tündra lookup"""

    if not vn:
        print("Get own VNs")
        fn = "data/no-repetition.json"
        vn = read_vn(fn)
        print(len(vn))

    out = "result/no-repetition.txt"

    with open(out, "w") as f:
        for i in range(len(vn)):
            v = vn[i]
            item1 = v[0]
            item2 = v[1]
            word1 = v[2]
            word2 = v[3]

            url = 'https://weblicht.sfs.uni-tuebingen.de/Tundra/tuebadz-110-dp/{}?access=private '
            url1 = url.format(int(item1.sentence) + 1)
            url2 = url.format(int(item2.sentence) + 1)

            f.write(str(i + 1) + "\n")
            f.write(str(item1) + "\n")
            f.write(str(item2) + "\n")
            f.write(word1 + " - " + word2 + "\n")
            f.write(url1 + "\n")
            f.write(url2 + "\n")
            f.write("\n")


def get_sentence_ids(filename: str):
    """returns the set of sentence ids (no duplicates)"""
    vn = read_vn(filename)
    print(len(vn))
    sentences = set()
    for v in vn:
        sentences.add(v[0].sentence + 1)
        sentences.add(v[1].sentence + 1)
    return sentences


def get_label_pair_statistics(filename: str):
    """returns the counts for the label pairs"""
    vn = read_vn(filename)
    pairs = list()
    for v in vn:
        label1 = v[0].get_label_str()
        label2 = v[1].get_label_str()
        label1 = label1[:-2]
        if label2 != "NIL":
            label2 = label2[:-2]

        # this allows me to ignore the vice-versa versions
        if (label2, label1) in pairs:
            pairs.append((label2, label1))
        else:
            pairs.append((label1, label2))

    counter = Counter(pairs)
    return counter.most_common()


def get_label_statistics(filename: str):
    """returns the counts for the labels themselves"""
    vn = read_vn(filename)
    labels = list()
    for v in vn:
        label1 = v[0].get_label_str()
        label2 = v[1].get_label_str()
        label1 = label1[:-2]
        if label2 != "NIL":
            label2 = label2[:-2]
        labels.append(label1)
        labels.append(label2)

    counter = Counter(labels)
    return counter.most_common()


def most_frequent_sentences(filename: str):
    """returns the sentence ids that appear more than 10 times in the variation nuclei"""
    vn = read_vn(filename)
    sentences = list()
    for v in vn:
        sentences.append(v[0].sentence + 1)
        sentences.append(v[1].sentence + 1)

    counter = Counter(sentences)
    return counter.most_common(40)


def most_frequent_vn(filename: str):
    """returns a list of all word pairs which appear more than 10 times in the variation nuclei"""
    vn = read_vn(filename)
    items = list()
    for v in vn:
        item1 = v[0]
        item2 = v[1]
        cur1 = (str(item1.sentence + 1) + ';' + str(item1.word1) + ';' + str(item1.word2) + ';' + item1.get_label_str())
        cur2 = (str(item2.sentence + 1) + ';' + str(item2.word1) + ';' + str(item2.word2) + ';' + item2.get_label_str())
        items.append(cur1 + ';' + v[2] + ';' + v[3])
        items.append(cur2 + ';' + v[2] + ';' + v[3])

    counter = Counter(items)
    return counter.most_common(20)


def create_plots(filenames: list):
    """function to use matplotlib and pandas to create some plots"""

    # get label statistics for both sets
    stats1 = get_label_pair_statistics(filenames[0])
    stats2 = get_label_pair_statistics(filenames[1])

    # plot input lists for first set
    labels1 = [la[0][0] + " - " + la[0][1] for la in stats1][:20]
    label_counts1 = [la[1] for la in stats1][:20]
    labels1.reverse()
    label_counts1.reverse()

    # plot input lists for second set
    labels2 = [la[0][0] + " - " + la[0][1] for la in stats2][:20]
    label_counts2 = [la[1] for la in stats2][:20]
    labels2.reverse()
    label_counts2.reverse()

    # same for both sets
    indexes = np.arange(0, len(labels1))
    width = 0.8

    # set figure dimensions
    fig, axis = plt.subplots(1, 2)
    fig.set_figheight(7)
    fig.set_figwidth(15)

    # bar plot - first set
    plt.subplot(1, 2, 1)
    plt.title("Full", fontsize=17, pad=12)
    plt.barh(indexes, label_counts1, width, color="darkblue")
    plt.yticks(indexes, labels1, fontsize=11)
    plt.tight_layout()
    plt.margins(0.05, 0.01)

    # bar plot - second set
    plt.subplot(1, 2, 2)
    plt.title("No-Repetition", fontsize=17, pad=10)
    plt.barh(indexes, label_counts2, width, color="darkgreen")
    plt.yticks(indexes, labels2, fontsize=11)
    plt.tight_layout()
    plt.margins(0.05, 0.01)

    plt.subplots_adjust(left=0.12, bottom=0.12, wspace=0.35)
    fig.text(0.5, 0.02, "Frequency", ha='center', fontsize=17)
    fig.text(0.01, 0.5, "UD Label", va='center', rotation='vertical', fontsize=17)

    # fig.savefig("plots/labelPair_distribution.pdf")
    fig.show()


if __name__ == "__main__":
    collect_statistics('data/variationNuclei.json')
