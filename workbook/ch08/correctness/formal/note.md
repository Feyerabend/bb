Let:

- $s$ and $t$ be strings
- \(|s|\) and \(|t|\) their lengths
- $\text{start} \in \mathbb{N}$, $1 \leq \text{start} \leq |s| + 1$
- $\text{instr}(\text{start}, s, t) = r \in \mathbb{N}$

The definition of $r$ is:

$$
r = 0 \iff \neg \exists i \in \mathbb{N},\ \text{start} \leq i \leq |s| - |t| + 1 \text{ such that } \forall j \in [0, |t|-1],\ s[i + j] = t[j + 1]
$$

$$
r \neq 0 \iff \exists i \in \mathbb{N},\ \text{start} \leq i \leq |s| - |t| + 1 \text{ such that } \forall j \in [0, |t|-1],\ s[i + j] = t[j + 1] \wedge \forall k \in \mathbb{N},\ (\text{start} \leq k < i) \implies \exists j \in [0, |t|-1],\ s[k + j] \neq t[j + 1]
$$


*Explanation:*

- If $r = 0$, no substring of $s$ starting at or after \(\text{start}\) matches $t$.
- If $r \neq 0$, then $r$ is the smallest index $i$ such that the substring of $s$ starting at $i$ equals $t$.
- The indices are 1-based.
- The notation $s[x]$ means the character at position $x$ in $s$.


In BASIC, INSTR(start, string1, string2) returns the position (1-based) of the first occurrence of string2 within string1 starting from position start. If string2 is not found, it returns 0.



```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1), st.text(), st.text())
def test_instr_properties(start, string1, string2):
    # Assume start valid (or handle in function)
    start = max(1, start)
    pos = instr(start, string1, string2)

    # Property 1: empty string2
    if string2 == "":
        assert pos == start

    # Property 2: start out of bounds
    if start > len(string1) + 1:
        assert pos == 0

    # Property 3: substring match at pos
    if pos != 0:
        # pos is 1-based, adjust for Python 0-based indexing
        assert string1[pos-1 : pos-1 + len(string2)] == string2

    # Property 4: pos >= start or zero
    assert pos == 0 or pos >= start
```




```python
def instr(start, string1, string2):
    """
    Find the position of string2 within string1, starting from position start.
    
    Args:
        start: 1-based starting position to begin search
        string1: string to search in
        string2: substring to search for
    
    Returns:
        1-based position of first occurrence of string2 in string1 at or after start,
        or 0 if not found
    """
    # Handle edge cases
    if start < 1:
        start = 1
    
    if start > len(string1) + 1:
        return 0
    
    if string2 == "":
        return start
    
    # Convert to 0-based indexing for Python string operations
    start_idx = start - 1
    
    # Search for substring starting from start position
    pos = string1.find(string2, start_idx)
    
    # Convert back to 1-based indexing, or return 0 if not found
    return pos + 1 if pos != -1 else 0



# Property-based tests using Hypothesis
from hypothesis import given, strategies as st

@given(st.integers(min_value=1), st.text(), st.text())
def test_instr_properties(start, string1, string2):
    # Ensure start is valid (or handle in function)
    start = max(1, start)
    pos = instr(start, string1, string2)

    # Property 1: empty string2
    if string2 == "":
        assert pos == start

    # Property 2: start out of bounds
    if start > len(string1) + 1:
        assert pos == 0

    # Property 3: substring match at pos
    if pos != 0:
        # pos is 1-based, adjust for Python 0-based indexing
        assert string1[pos-1 : pos-1 + len(string2)] == string2

    # Property 4: pos >= start or zero
    assert pos == 0 or pos >= start


# Additional unit tests for specific cases
def test_instr_examples():
    """Test specific examples to verify behavior"""
    # Basic substring search
    assert instr(1, "hello world", "world") == 7
    assert instr(1, "hello world", "hello") == 1
    assert instr(1, "hello world", "xyz") == 0
    
    # Starting position tests
    assert instr(3, "hello hello", "hello") == 7
    assert instr(8, "hello world", "world") == 0
    
    # Edge cases
    assert instr(1, "", "test") == 0
    assert instr(1, "test", "") == 1
    assert instr(5, "test", "") == 5
    assert instr(10, "short", "test") == 0
    
    # Case sensitivity
    assert instr(1, "Hello", "hello") == 0
    
    print("All unit tests passed!")


if __name__ == "__main__":
    # Run unit tests
    test_instr_examples()
    
    # Run property-based tests
    print("Running property-based tests...")
    test_instr_properties()
    print("Property-based tests completed!")
    
    # Interactive examples
    print("\nExample usage:")
    print(f'instr(1, "hello world", "world") = {instr(1, "hello world", "world")}')
    print(f'instr(1, "hello world", "hello") = {instr(1, "hello world", "hello")}')
    print(f'instr(7, "hello world", "world") = {instr(7, "hello world", "world")}')
    print(f'instr(8, "hello world", "world") = {instr(8, "hello world", "world")}')
    print(f'instr(1, "test", "") = {instr(1, "test", "")}')
```

