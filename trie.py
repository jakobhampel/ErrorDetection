""" parts of this code are inspired from
https://towardsdatascience.com/implementing-a-trie-data-structure-in-python-in-less-than-100-lines-of-code-a877ea23c1a1
"""


class Node:
    """represents a node in a Trie"""
    def __init__(self, word: str):
        self.children = []
        self.word = word
        self.is_finished = False

    def add_node(self, node):
        self.children.append(node)


class Trie:
    """implementation of a trie storing word pairs word-wise"""
    def __init__(self):
        self.root = Node('*')

    def add_pair(self, word_pair: tuple):
        """ adds a word pair to the trie """
        node = self.root
        for word in word_pair:
            found = False
            for child in node.children:
                if child.word == word:
                    node = child
                    found = True
                    break
            if not found:
                new_node = Node(word)
                node.add_node(new_node)
                node = new_node
        node.is_finished = True

    def clear(self):
        self.root = Node('*')

    def find_pair(self, word_pair: tuple):
        """ searches for a word pair in the trie"""

    def pretty_print(self):
        """ pretty prints the two levels of the trie"""
        for child in self.root.children:
            print(child.word)
            for grandchild in child.children:
                print("\t" + grandchild.word)
                for grandgrandchild in grandchild.children:
                    print("\t\t" + grandgrandchild.word)


if __name__ == "__main__":
    trie = Trie()
    with open("test/trietest.txt", 'r', encoding='utf8') as f:
        lines = f.readlines()

    for line in lines:
        pair = tuple(line.split(" "))
        trie.add_pair(pair)
    trie.pretty_print()

