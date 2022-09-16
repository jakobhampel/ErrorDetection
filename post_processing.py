"""offers functions to compare two json files of variation nuclei and detect the differences"""
import json
from trie import Item


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
    fn = "data/variationNuclei.json"
    vn = read_vn(fn)
    print(len(vn))
    result = list()
    for v in vn:
        item1 = v[0]
        if len(item1.label) > 1:
            result.append(v)
    convert_to_txt(result)


def compare_results():
    version1 = "data/variationNuclei2.json"
    version2 = "data/variationNuclei4.json"

    vn1 = read_vn(version1)
    vn2 = read_vn(version2)

    result = list()
    for v in vn1:
        if v not in vn2:
            result.append(v)

    convert_to_txt(result)


def convert_to_txt(vn: list = None):

    if not vn:
        print("Get own VNs")
        fn = "data/variationNuclei.json"
        vn = read_vn(fn)
        print(len(vn))

    out = "result/variationNuclei.txt"

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


if __name__ == "__main__":
    convert_to_txt()
