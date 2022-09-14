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

        item1 = Item(i1[0], i1[1], i1[2], set(i1[3]) if i1[3] else None)
        item2 = Item(i2[0], i2[1], i2[2], set(i2[3]) if i2[3] else None)
        result.append([item1, item2])
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
        fn = "data/vadriationNuclei1.json"
        vn = read_vn(fn)
        print(len(vn))

    out = "result/variationNuclei_2without4.txt"

    with open(out, "w") as f:
        sub = 0
        for i in range(len(vn)):
            v = vn[i]
            item1 = v[0]
            item2 = v[1]

            if item1.sentence in {9378, 17076, 34302, 43704}:
                if item2.sentence in {901, 17065, 34301, 43686} and item2.label:
                    sub -= 1
                    continue

            url = 'https://weblicht.sfs.uni-tuebingen.de/Tundra/tuebadz-110-dp/{}?access=private '
            url1 = url.format(int(item1.sentence) + 1)
            url2 = url.format(int(item2.sentence) + 1)

            f.write(str(i + 1 + sub) + "\n")
            f.write(str(item1) + "\n")
            f.write(str(item2) + "\n")
            f.write(url1 + "\n")
            f.write(url2 + "\n")
            f.write("\n")

        print(sub)


if __name__ == "__main__":
    compare_results()
