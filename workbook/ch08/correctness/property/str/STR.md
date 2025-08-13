
1. Associativity

Hypothesis (property-based):
```python
from hypothesis import given, strategies as st

@given(st.text(), st.text(), st.text())
def test_string_concatenation_associativity(a, b, c):
    assert (a + b) + c == a + (b + c)
```
Classic (example-based):
```python
def test_string_concatenation_associativity_classic():
    cases = [
        ("a", "b", "c"),
        ("", "foo", "bar"),
        ("x", "", "y"),
        ("", "", ""),
        ("hello", " ", "world")
    ]
    for a, b, c in cases:
        assert (a + b) + c == a + (b + c)
```



2. Identity (empty string)

Hypothesis:
```python
@given(st.text())
def test_string_concatenation_identity(s):
    assert s + "" == s
    assert "" + s == s
```
Classic:
```python
def test_string_concatenation_identity_classic():
    cases = ["", "a", "foo", " "]
    for s in cases:
        assert s + "" == s
        assert "" + s == s
```



3. Length additivity

Hypothesis:
```python
@given(st.text(), st.text())
def test_string_concatenation_length(a, b):
    assert len(a + b) == len(a) + len(b)
```
Classic:
```python
def test_string_concatenation_length_classic():
    cases = [
        ("a", "b"),
        ("", "foo"),
        ("bar", ""),
        ("hello", "world")
    ]
    for a, b in cases:
        assert len(a + b) == len(a) + len(b)
```



4. Double reversal

Hypothesis:
```python
@given(st.text())
def test_string_reverse_twice(s):
    assert s[::-1][::-1] == s
```
Classic:
```python
def test_string_reverse_twice_classic():
    cases = ["", "a", "abc", "hello world"]
    for s in cases:
        assert s[::-1][::-1] == s
```



5. Substring property

Hypothesis:
```python
@given(st.text(), st.text())
def test_string_substring_property(a, b):
    concatenated = a + b
    assert a in concatenated
    assert b in concatenated
```
Classic:
```python
def test_string_substring_property_classic():
    cases = [
        ("a", "b"),
        ("", "foo"),
        ("bar", ""),
        ("hello", "world")
    ]
    for a, b in cases:
        concatenated = a + b
        assert a in concatenated
        assert b in concatenated
```



Hypothesis: generates many random cases automatically, potentially uncovering edge cases you didn’t think of.
Classic: you pick a finite set of examples manually, so some edge cases may be missed.
Both use assert to check correctness.
