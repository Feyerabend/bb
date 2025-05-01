def calculate_hash(s, length):
    hash_value = 0
    for i in range(length):
        hash_value = (hash_value * 256 + ord(s[i])) % 101  # prime 101
    return hash_value

def recalculate_hash(s, old_index, new_index, old_hash, pattern_length):
    new_hash = (old_hash - ord(s[old_index]) * (256 ** (pattern_length - 1))) % 101
    new_hash = (new_hash * 256 + ord(s[new_index])) % 101
    return new_hash if new_hash >= 0 else new_hash + 101

def rabin_karp_search(text, pattern):
    text_length = len(text)
    pattern_length = len(pattern)

    pattern_hash = calculate_hash(pattern, pattern_length)
    text_hash = calculate_hash(text, pattern_length)

    for i in range(text_length - pattern_length + 1):
        if pattern_hash == text_hash:
            if text[i:i + pattern_length] == pattern:
                print(f"Pattern found at index {i}")

        if i < text_length - pattern_length:
            text_hash = recalculate_hash(text, i, i + pattern_length, text_hash, pattern_length)


text = "ABABDABACDABABCABAB"
pattern = "ABABCABAB"

print(f"Text: {text}")
print(f"Pattern: {pattern}")

rabin_karp_search(text, pattern)
