def compute_prefix_table(pattern):
    pattern_length = len(pattern)
    prefix_table = [0] * pattern_length
    length = 0  # length of previous longest prefix suffix

    for i in range(1, pattern_length):
        while length > 0 and pattern[i] != pattern[length]:
            length = prefix_table[length - 1]

        if pattern[i] == pattern[length]:
            length += 1
            prefix_table[i] = length

    return prefix_table

def kmp_search(text, pattern):
    text_length = len(text)
    pattern_length = len(pattern)
    prefix_table = compute_prefix_table(pattern)

    i = 0  # index for text
    j = 0  # index for pattern

    while i < text_length:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == pattern_length:
            print(f"Pattern found at index {i - j}")
            j = prefix_table[j - 1]
        elif i < text_length and pattern[j] != text[i]:
            if j != 0:
                j = prefix_table[j - 1]
            else:
                i += 1


text = "ABABDABACDABABCABAB"
pattern = "ABABCABAB"

print(f"Text: {text}")
print(f"Pattern: {pattern}")

kmp_search(text, pattern)
