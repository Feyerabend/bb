import re

def soundex(name):
    if not name:
        return ""
    
    # to uppercase and remove non-letters
    name = re.sub(r'[^A-Z]', '', name.upper())
    if not name:
        return ""
    
    # keep first letter
    first_letter = name[0]
    name = name[1:]
    
    # digit mapping
    soundex_digits = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }
    
    # letters to digits
    digits = []
    for letter in name:
        digit = soundex_digits.get(letter, '')
        if digit and (not digits or digits[-1] != digit):
            digits.append(digit)
    
    # pad with zeros or truncate to get 3 digits
    digits = (digits + ['0'] * 3)[:3]
    
    # return Soundex code: first letter + 3 digits
    return first_letter + ''.join(digits)

