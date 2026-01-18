
# Design patterns used:
# - Factory Pattern: to create collections
# - Command Pattern: to encapsulate each operation (Insert, Find, Update, Delete) as command objects
# - Strategy Pattern: to abstract the query-matching logic, allowing future support for $gt, $in, etc.
# - Facade Pattern: to provide a simple unified API (NoSQLDatabase) over the underlying command system

from abc import ABC, abstractmethod


class MatchStrategy(ABC):
    @abstractmethod
    def matches(self, document: dict, query: dict) -> bool:
        pass

class ExactMatchStrategy(MatchStrategy):
    def matches(self, document: dict, query: dict) -> bool:
        return all(k in document and document[k] == v for k, v in query.items())


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

class InsertCommand(Command):
    def __init__(self, collection, document):
        self.collection = collection
        self.document = document

    def execute(self):
        self.collection.append(self.document)

class FindCommand(Command):
    def __init__(self, collection, query, strategy: MatchStrategy):
        self.collection = collection
        self.query = query
        self.strategy = strategy

    def execute(self):
        if self.query is None:
            return list(self.collection)
        return [doc for doc in self.collection if self.strategy.matches(doc, self.query)]

class UpdateCommand(Command):
    def __init__(self, collection, query, updates, strategy: MatchStrategy):
        self.collection = collection
        self.query = query
        self.updates = updates
        self.strategy = strategy

    def execute(self):
        for doc in self.collection:
            if self.strategy.matches(doc, self.query):
                doc.update(self.updates)

class DeleteCommand(Command):
    def __init__(self, collection, query, strategy: MatchStrategy):
        self.collection = collection
        self.query = query
        self.strategy = strategy

    def execute(self):
        self.collection[:] = [doc for doc in self.collection if not self.strategy.matches(doc, self.query)]


class CollectionFactory:
    def create(self):
        return []


class NoSQLDatabase:
    def __init__(self):
        self._collections = {}
        self._match_strategy = ExactMatchStrategy()
        self._collection_factory = CollectionFactory()

    def create_collection(self, name):
        if name not in self._collections:
            self._collections[name] = self._collection_factory.create()

    def _get_collection(self, name):
        if name not in self._collections:
            raise ValueError("Collection does not exist")
        return self._collections[name]

    def insert(self, collection_name, document):
        collection = self._get_collection(collection_name)
        cmd = InsertCommand(collection, document)
        cmd.execute()

    def find(self, collection_name, query=None):
        collection = self._get_collection(collection_name)
        cmd = FindCommand(collection, query, self._match_strategy)
        return cmd.execute()

    def update(self, collection_name, query, updates):
        collection = self._get_collection(collection_name)
        cmd = UpdateCommand(collection, query, updates, self._match_strategy)
        cmd.execute()

    def delete(self, collection_name, query):
        collection = self._get_collection(collection_name)
        cmd = DeleteCommand(collection, query, self._match_strategy)
        cmd.execute()


if __name__ == '__main__':
    db = NoSQLDatabase()
    db.create_collection("users")

    db.insert("users", {"id": 1, "name": "Alice", "age": 25})
    db.insert("users", {"id": 2, "name": "Bob", "age": 30})

    print("ALL:", db.find("users"))
    print("FIND:", db.find("users", {"name": "Bob"}))

    db.update("users", {"name": "Bob"}, {"age": 31})
    print("UPDATED:", db.find("users", {"name": "Bob"}))

    db.delete("users", {"id": 2})
    print("AFTER DELETE:", db.find("users"))
