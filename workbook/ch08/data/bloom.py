
class BloomFilter:
    def __init__(self, size, hash_count):
        self.size = size  # size of bit array
        self.hash_count = hash_count  # num of hash functions
        self.bit_array = [0] * size  # init the bit array with 0's

    def _hash(self, item, seed):
        # simple hash function: based on Python's built-in hash function
        hash_value = hash(str(seed) + item) % self.size
        return hash_value

    def add(self, item):
        for i in range(self.hash_count):
            index = self._hash(item, i)
            self.bit_array[index] = 1  # set the bit at calculated index to 1

    def check(self, item):
        for i in range(self.hash_count):
            index = self._hash(item, i)
            if self.bit_array[index] == 0:
                return False  # if any bit is 0, the item is definitely not in the set
        return True  # if all bits are 1, the item might be in the set

# example
bf = BloomFilter(size=1000, hash_count=3)
bf.add("apple")
bf.add("banana")

# test
print(bf.check("apple"))  # True, since "apple" was added
print(bf.check("banana"))  # True, since "banana" was added
print(bf.check("grape"))  # False, "grape" was not added (but might return True due to false positives)
