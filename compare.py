"""offers functions to compare two json files of variation nuclei and detect the differences"""
import json


def read_vn(filename):
    """loads the variation nuclei from a json file"""
    result = list()
    with open(filename, "r") as fp:
        variation_nuclei = json.load(fp)
    for vn in variation_nuclei:
        i1 = vn[0]
        i2 = vn[1]

        item1 = i1[0], i1[1], i1[2], set(i1[3])
        item2 = i2[0], i2[1], i2[2], set(i2[3])
        result.append([item1, item2])
    return result


def compare_results():
    version1 = "data/variationNuclei1.json"
    version2 = "data/variationNuclei2.json"

    vn1 = read_vn(version1)
    vn2 = read_vn(version2)

    result = list()
    for v in vn2:
        if v not in vn1:
            result.append(v)

    print(len(result))
    for r in result:
        print(r)
        print("https://weblicht.sfs.uni-tuebingen.de/Tundra/tuebadz-110-dp/{}?access=private ".format(str(int(r[0][0]) + 1)))
        print("https://weblicht.sfs.uni-tuebingen.de/Tundra/tuebadz-110-dp/{}?access=private ".format(str(int(r[1][0]) + 1)))
        print("\n")


if __name__ == "__main__":
    compare_results()
