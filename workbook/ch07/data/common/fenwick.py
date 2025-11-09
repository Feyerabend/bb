class FenwickTree:
    def __init__(self, size):
        self.size = size
        self.tree = [0] * (size + 1)

    def update(self, index, delta):
        while index <= self.size:
            self.tree[index] += delta
            index += index & -index

    def prefix_sum(self, index):
        sum_ = 0
        while index > 0:
            sum_ += self.tree[index]
            index -= index & -index
        return sum_

    def range_sum(self, left, right):
        return self.prefix_sum(right) - self.prefix_sum(left - 1)


ft = FenwickTree(10)
ft.update(1, 5)
ft.update(3, 7)
ft.update(7, 4)

print("Prefix sum up to index 3:", ft.prefix_sum(3))
print("Sum from index 2 to 7:", ft.range_sum(2, 7))