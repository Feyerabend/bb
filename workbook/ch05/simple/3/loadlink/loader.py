
class LibraryLoader:
    def __init__(self):
        self.libraries = { }

    # loading ..
    def add_library(self, name, program):
        if name in self.libraries:
            raise ValueError(f"Library '{name}' is already loaded.")
        self.libraries[name] = program

    def get_library(self, name):
        if name not in self.libraries:
            raise ValueError(f"Library '{name}' not found.")
        return self.libraries[name]

    # linking ..
    def link_library(self, vm, library_name):
        library = self.get_library(library_name)
        vm.program += library # yes, simple linking
        vm.preprocess_labels()  # ensure labels are correctly linked after adding library
