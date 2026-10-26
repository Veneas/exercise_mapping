import bisect
import random

# =-=-=-=-=-=-=-=-= Task 1 =-=-=-=-=-=-=-=-=
def brute_force(text, p):
    """
    Finding every start pos of p in text by checking each position.
    :param text:
    :param p:
    :return:
    """

    positions = []
    # Iterating up to where the pattern can fully fit
    for i in range(len(text) - len(p) + 1):
        if text[i:i+len(p)] == p:
            positions.append(i)

    return positions


def suffix_array(text):
    """
    Generates the suffix array by sorting the starting positions of all suffixes
    :param text:
    :return:
    """

    # Creating a list of all possible start positions
    positions = list(range(len(text)))

    # Sorting the pos based on the actual string suffix that starts here
    return sorted(positions, key=lambda i: text[i:])


def find_block(text, sa, p):
    """
    Uses binary search to find the block of rows in the suffix array whose
    suffixes start with the pattern p.
    :param text:
    :param sa:
    :param p:
    :return:
    """
    class SuffixComparer:
        """
        Helper class to allow Python bisecs module to binary search the
        suffix array without explicitly copying strings.
        """
        def __init__(self, text, sa, length):
            self.text = text
            self.sa = sa
            self.length = length


        def __getitem__(self, i):
            """ Return just enough of the suffix to compare agianst pattern"""
            start = self.sa[i]
            return self.text[start:start + self.length]


        def __len__(self):
            return len(self.sa)

    # Using bisecd to find the leftmost/rightmost insertion poitns
    comparer = SuffixComparer(text, sa, len(p))

    a = bisect.bisect_left(comparer, p)
    b = bisect.bisect_right(comparer, p)

    return a, b

# =-=-=-=-=-=-=-=-= MAIN =-=-=-=-=-=-=-=-=
if __name__ == '__main__':
    print("=-=-=-=-=-=-=-=-= TASK 1 =-=-=-=-=-=-=-=-=")

    # Examples
    test_text = "monkeyeatsbananainbananaland$"
    test_pattern = "an"

    print(f"Test text: {test_text}")
    print(f"Test pattern: {test_pattern}")

    # Brute force
    brute = brute_force(test_text, test_pattern)
    print(f"Brute force result: {brute}")

    # Suffix array
    sa = suffix_array(test_text)
    print("Row | Pos | Suffix")
    for i, pos in enumerate(sa):
        print(f"{i:3} | {pos:3} | {test_text[pos:]}")

    # Find block
    a, b = find_block(test_text, sa, test_pattern)
    print(f"\nBlock found between rows [{a}, {b}]")

    # Extracting the pos from the rows
    block_positions = sorted(sa[a:b])
    print(f"Block positions: {block_positions}")

    # Verifying the match
    print(f"Brute force matches block ? {brute == block_positions}")





