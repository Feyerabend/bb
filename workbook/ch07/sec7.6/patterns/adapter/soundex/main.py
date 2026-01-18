from soundex import soundex
from database import NameDatabase
from adapter import DatabaseSoundexAdapter, PhoneticMatcher

class SoundexNameMatcher:
    def __init__(self, phonetic_matcher):
        self.phonetic_matcher = phonetic_matcher
    
    def find_name_matches(self, input_name):
        phonetic_code = soundex(input_name)
        if not phonetic_code:
            return None, []
        matches = self.phonetic_matcher.find_matches(phonetic_code)
        return phonetic_code, matches

def main():
    database = NameDatabase()
    
    # adapter to connect database to Soundex matcher
    adapter = DatabaseSoundexAdapter(database)
    
    # init Soundex matcher with the adapter
    matcher = SoundexNameMatcher(adapter)
    
    print("Enter a name to find Soundex matches with phone numbers (or 'quit' to exit):")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == 'quit':
            break
            
        if not user_input:
            print("Please enter a valid name.")
            continue
            
        # matches using Soundex
        phonetic_code, matches = matcher.find_name_matches(user_input)
        if not phonetic_code:
            print("Invalid name entered.")
            continue
            
        print(f"\nSoundex code for '{user_input}': {phonetic_code}")
        if matches:
            print("Matches found:")
            for name, phone in matches:
                print(f"  Name: {name}, Phone: {phone}")
        else:
            print("No matches found.")

if __name__ == "__main__":
    main()

