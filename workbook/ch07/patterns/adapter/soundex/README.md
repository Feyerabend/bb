
## Soundex

Soundex is a phonetic algorithm developed to index words--especially names--by their sound
when pronounced in English. The goal is to group together names that sound alike but are
spelled differently. For example, "Smith" and "Smyth" would be considered equivalent in Soundex.

It was originally developed by Robert C. Russell and Margaret K. Odell and patented in 1918
and 1922. The U.S. National Archives later adopted it, and it has been widely used in genealogy,
databases, and record linkage systems.[^names]

[^names]: IN the example I've used names from https://github.com/aruljohn/popular-baby-names/tree/master/1900.

### How It Works

Soundex converts a name into a 4-character code:
1. The first letter of the name is kept as-is.
2. The remaining letters are encoded as digits according to a phonetic group:

```
B, F, P, V → 1
C, G, J, K, Q, S, X, Z → 2
D, T → 3
L → 4
M, N → 5
R → 6
```

3. Vowels (A, E, I, O, U), H, W, and Y are ignored (unless they're the first letter).
4. Adjacent letters that map to the same number are not duplicated.
5. The result is padded with zeros or truncated to ensure exactly 4 characters.

Example:
```
Name: Robert
Step 1: R (keep first letter)
Step 2: O (ignored), B → 1, E (ignored), R → 6, T → 3
Encoded: R163
```

### Use Cases

1. Genealogy Databases:
Soundex was heavily used in indexing the U.S. Census records (1880-1920). Researchers can search for
ancestors even if the spelling of their names has changed.

2. Fuzzy Name Matching:
Useful in systems where exact spelling isn't guaranteed:
- Voter registration
- Credit checks
- Law enforcement databases
- Data deduplication

3. Linguistic Search Systems:
Early search engines and linguistic research tools used Soundex to match user queries phonetically.

4. Misspelling Correction:
Helps in identifying typographical errors in names or detecting duplicates in forms and documents.


Limitations
- It works only for English pronunciation, so it's less effective for names from non-English languages.
- It generates many false positives (different-sounding names mapping to the same code).
- It may miss some phonetic matches due to rigid rules (e.g., ignoring vowels).



### Modern Context

Modern systems often prefer more sophisticated algorithms like:
- Metaphone / Double Metaphone
- Levenshtein Distance
- Jaro-Winkler Distance

But Soundex remains a useful, efficient, and historically important technique for basic phonetic matching,
especially when dealing with legacy datasets.


### Adapter Pattern


__Incompatible Interfaces__

- *Problem*: The SoundexNameMatcher (client) expects to query names using phonetic codes via a
  PhoneticMatcher interface (find_matches(phonetic_code)), but the NameDatabase (adaptee) provides
  an incompatible interface with methods for exact name lookup (get_phone_by_name) or retrieving
  all names (get_all_names).

- *Solution*: The DatabaseSoundexAdapter bridges this gap by implementing PhoneticMatcher and
  translating phonetic code queries into database operations (computing Soundex codes for all
  names and filtering matches).

- *Alignment*: This directly aligns with the Adapter Pattern's purpose: adapting one interface
  (database's name-based lookup) to another (phonetic code-based lookup) without modifying either
  component.

__Separation of Concerns__

- The SoundexNameMatcher focuses solely on generating Soundex codes and delegating queries to the
  PhoneticMatcher interface, unaware of the database's implementation.

- The NameDatabase handles data storage and retrieval without knowing about Soundex or phonetic matching.

- The DatabaseSoundexAdapter encapsulates the logic to compute Soundex codes and match them,
  keeping the client and adaptee independent.

*Alignment*: This modularity demonstrates the pattern's goal of enabling collaboration between components
with distinct responsibilities.

__Reusability and Extensibility__

The PhoneticMatcher interface allows the SoundexNameMatcher to work with any data source
(e.g., a CSV file, SQLite database, or API) as long as an adapter implements find_matches.

For example, you could create a new adapter for a real database (e.g., SQLite) without
changing SoundexNameMatcher or soundex.py.

*Alignment*: This showcases the pattern's strength in making systems flexible and reusable,
a key benefit of adapters.

The use case mimics a realistic scenario: integrating a phonetic matching system (Soundex) with a data storage
system (database) that wasn't designed for phonetic queries. This is common in legacy systems or when combining
third-party components.

