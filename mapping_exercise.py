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


# =-=-=-=-=-=-=-=-= Task 2 =-=-=-=-=-=-=-=-=
def bwt(text, sa):
    """
    Computing the Burrows-Wheeler Transform (BWT) of a text using its suffix array.
    :param text:
    :param sa:
    :return:
    """

    # For sa[row] == 0, text [0-1] evaluates to text[-1], which correcly grabs
    # the $ at the end of the string.
    return "".join(text[pos-1] for pos in sa)


def first_occurrence(letters):
    """
    Finds the first row index ( in the end of the F column) for each character.
    :param letters:
    :return:
    """

     # Counting the total occurrences of each char
    counts = {}
    for char in letters:
        counts[char] = counts.get(char, 0) + 1

    first_occ = {}
    current_row = 0

    # Iterating through chars in alphabetical order
    for char in sorted(counts.keys()):
        first_occ[char] = current_row
        current_row += counts[char]

    return first_occ


def inverse_bwt(bwt_str):
    """
    Recovers the original text from its BWT using the last-to-first mapping
    :param bwt_str:
    :return:
    """

    # Computing the occurence number of every letter in the BWT (the L column)
    occ_counts = {}
    occurrences = []
    for char in bwt_str:
        occ_counts[char] = occ_counts.get(char, 0) + 1
        occurrences.append(occ_counts[char])

    # Gettig the first occ map for the sorted letters (F col)
    first_occ = first_occurrence(bwt_str)

    # Tracing backwards
    text_rev = []
    row = 0 # Starting at 0, which holds the $ suffix

    # We loop len(bwt_str) - 1 times because we manually append the $ at the end
    for _ in range(len(bwt_str) - 1):
        char = bwt_str[row]
        text_rev.append(char)

        # Last-to-first jump -> next row = first_occurence(char) + k - 1
        k = occurrences[row]
        row = first_occ[char] + k - 1

    # Reversing the collected string and add the terminal $
    return "".join(reversed(text_rev)) + "$"

# =-=-=-=-=-=-=-=-= Task 3 =-=-=-=-=-=-=-=-=
class FMIndex:
    def __init__(self, text, s):
        """
        Builds the FM-index for a given text and sampling step s.
        :param text:
        :param s:
        """

        self.s = s
        # Buidling the suffix array once, using it, and discarding it to save memory
        sa = suffix_array(text)

        # BWT & first occurence
        self.bwt = bwt(text, sa)
        self.first_occurrence = first_occurrence(self.bwt)

        # Samples suffix array
            # Keeping only the rows where the original text pos is a multiple of s
        self.sampled = {row: pos for row, pos in enumerate(sa) if pos % s == 0}

        # Counting array
            # counts[X][i] is the num of times letter X appears in self.bwt[:i]
        unique_chars = set(self.bwt)
        # Initialising the lists with zeros (length is len(bwt) + 1)
        self.counts = {char: [0] * (len(self.bwt) + 1) for char in unique_chars}

        # Populating counts in a single class
        for i, char in enumerate(self.bwt):
            # Carrying over all counts form the previous step
            for c in unique_chars:
                self.counts[c][i+1] = self.counts[c][i]
            # Increment the count for the specific char it just saw
            self.counts[char][i+1] += 1


    def lf(self, row):
        """
        Last-to-first mapping -> returns the row of the suffix that starts one
        position earlier in the original text.
        :param self:
        :param row:
        :return:
        """

        char = self.bwt[row]
        return self.first_occurrence[char] + self.counts[char][row]

    def count(self, p):
        """
        Backward search to find the [top, bottom) interval of rows that start with pattern p.
        :param self:
        :param p:
        :return:
        """

        top = 0
        bottom = len(self.bwt)

        # Searching backwards through the pattern
        for char in reversed(p):
            # If the char isnt even in the text, the patter doesnt exist
            if char not in self.first_occurrence:
                return (top, top)

            # Updating boundaries using the first occurrence and counts array
            top = self.first_occurrence[char] + self.counts[char][top]
            bottom = self.first_occurrence[char] + self.counts[char][bottom]

            # If the interval becomes empty, the pattern doesnt exist
            if top == bottom:
                return (top, top)


        return top, bottom

    def locate(self, p):
        """
        Finds the actual text positions of all occurrences of p.
        :param self:
        :param p:
        :return:
        """

        top, bottom = self.count(p)
        positions = []

        for row in range(top, bottom):
            curr_row = row
            steps = 0

            # Stepping backwards through the text using LF mapping until hitting a checkpoint
            while curr_row not in self.sampled:
                curr_row = self.lf(curr_row)
                steps += 1

            # The original pos is the checkpoint pos + the steps taken
            actual_pos = self.sampled[curr_row] + steps
            positions.append(actual_pos)

        return positions






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



    print("\n=-=-=-=-=-=-=-=-= TASK 2 =-=-=-=-=-=-=-=-=")
    cat_text = "CAT$"
    cat_sa = suffix_array(cat_text)
    cat_bwt = bwt(cat_text, cat_sa)

    print(f"Text: {cat_text}")
    print(f"BWT: {cat_bwt}")
    print(f"First occurence: {first_occurrence(cat_bwt)}")
    print(f"Inverse BWT: {inverse_bwt(cat_bwt)}")

    # Test with the longer string
    bwt_result = bwt(test_text, sa)
    recovered = inverse_bwt(bwt_result)
    print(f"\nLong text: {test_text}")
    print(f"BWT: {bwt_result}")
    print(f"Recovered text: {recovered}")
    print(f"Matches original? {recovered == test_text}")

    print("\n=-=-=-=-=-=-=-=-= TASK 3 =-=-=-=-=-=-=-=-=")
    fm = FMIndex("CAT$", 2)

    print("FMIndex for CAT$ (s=2):")
    print(f"BWT: {fm.bwt}")
    print(f"Counts for 'T': {fm.counts['T']}")
    print(f"Sampled SA: {fm.sampled}")

    # Test LF mapping (row 1 is AT$, row 2 is CAT$)
    print(f"\n LF mapping for row 1: {fm.lf(1)} (Expected: 2)")

    # Testing backward search count
    pattern = "AT"
    top, bottom = fm.count(pattern)
    print(f"Count for '{pattern}': ({top}, {bottom}) (Expected: (1, 2))")

    # testing locate
    locations = fm.locate(pattern)
    print(f"Locate '{pattern}': {locations} (Expected: [1]")



