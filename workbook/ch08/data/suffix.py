def build_suffix_array(text):
    n = len(text)
    # Create a list of tuples containing suffixes and their indices
    suffixes = [(text[i:], i) for i in range(n)]
    # Sort the suffixes lexicographically
    suffixes.sort()
    # Extract the sorted indices
    suffix_array = [suffix[1] for suffix in suffixes]
    return suffix_array

def longest_common_prefix(str1, str2):
    length = 0
    while length < len(str1) and length < len(str2) and str1[length] == str2[length]:
        length += 1
    return length

def longest_repeated_substring(text):
    n = len(text)

    # Build the suffix array
    suffix_array = build_suffix_array(text)

    # Find the longest common prefix between adjacent suffixes
    max_length = 0
    start_index = 0

    for i in range(n - 1):
        lcp = longest_common_prefix(text[suffix_array[i]:], text[suffix_array[i + 1]:])
        if lcp > max_length:
            max_length = lcp
            start_index = suffix_array[i]

    # If no repeated substring is found, return an empty string
    if max_length == 0:
        return ""

    # Extract the longest repeated substring
    result = text[start_index:start_index + max_length]
    return result

# Example usage
text = "abracadabra"
print("Text:", text)

# Find the longest repeated substring
result = longest_repeated_substring(text)

if result:
    print("Longest Repeated Substring:", result)
else:
    print("No repeated substring found.")
