
from soundex import soundex

class PhoneticMatcher:
    def find_matches(self, phonetic_code):
        raise NotImplementedError

class DatabaseSoundexAdapter(PhoneticMatcher):
    def __init__(self, database):
        self.database = database
    
    def find_matches(self, phonetic_code):
        matches = []
        for name, phone in self.database.get_all_names():
            if soundex(name) == phonetic_code:
                matches.append((name, phone))
        return matches
