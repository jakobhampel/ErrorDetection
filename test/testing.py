import sys
from trie import Trie
from error_detection import ErrorDetector

DEPENDENCY_PAIRS = {
                    ("root", "Veruntreute"): ("root-L", 1),
                    ("die", "AWO"): ("det-R", 1),
                    ("Veruntreute", "AWO"): ("nsubj-L", 1),
                    ("Veruntreute", "Spendengeld"): ("obj-L", 1),
                    ("Es", "gibt"): ("nsubj-R", 2),
                    ("root", "gibt"): ("root-L", 2),
                    ("so", "Buchung"): ("advmod-R", 2),
                    ("eine", "Buchung"): ("det-R", 2),
                    ("gibt", "Buchung"): ("obj-L", 2),
                    ("Ein", "Mitarbeiter"): ("det-R", 3),
                    ("root", "Mitarbeiter"): ("root-L", 3),
                    ("der", "Bank"): ("det-R", 3),
                    ("Mitarbeiter", "Bank"): {("nmod:poss-L", 3), ("obl-L", 3)},
                    ("auf", "Bank"): ("case-R", 3),
                    ("der", "Bank"): ("det-R", 3),
                    }


def test_trie():
    trie = Trie()
    with open("trietest.txt", 'r', encoding='utf8') as f:
        lines = f.readlines()

    for line in lines:
        pair = tuple(line.split(" "))
        trie.add_pair(pair)
    trie.pretty_print()


def test_dependency_pairs():
    ed = ErrorDetector()
    ed.detect_errors("TuebaDZ_test.txt")

    for key, value in DEPENDENCY_PAIRS.items():
        if key in ed.nuclei:
            vs = ed.nuclei[key]
            found = False
            for v in vs:
                if v == value:
                    found = True
            if not found:
                print("The nucleus ", end="")
                print(key[0] + " " + key[1], end="")
                print(" was found but instead of the correct label ")
                print(value)
                print("\n I only found these:\n")
                for v in vs:
                    print(v)
                sys.exit(1)
        else:
            print("The nucleus " + key[0] + " " + key[1] + " was not found")
            sys.exit(1)
    print("Success")


if __name__ == "__main__":
    test_dependency_pairs()
